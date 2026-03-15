'use strict';

/**
 * Preload script — runs in the renderer process with Node integration disabled.
 * Exposes a minimal, safe API surface to the web page via contextBridge.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('meetingMind', {
  /** App version string */
  version: process.env.npm_package_version || '2.0.0',

  /** Platform string: 'darwin' | 'win32' | 'linux' */
  platform: process.platform,

  /**
   * Open a URL in the system default browser.
   * Only http/https URLs are forwarded to the main process.
   * @param {string} url
   */
  openExternal: (url) => {
    if (typeof url === 'string' && /^https?:\/\//.test(url)) {
      ipcRenderer.send('open-external', url);
    }
  },

  /**
   * Listen for a one-time event from the main process.
   * Returns an unsubscribe function.
   * @param {string} channel
   * @param {Function} handler
   */
  on: (channel, handler) => {
    const ALLOWED_CHANNELS = ['server-ready', 'server-error'];
    if (!ALLOWED_CHANNELS.includes(channel)) return () => {};

    const wrapped = (_event, ...args) => handler(...args);
    ipcRenderer.on(channel, wrapped);
    return () => ipcRenderer.removeListener(channel, wrapped);
  },
});
