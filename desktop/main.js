'use strict';

const { app, BrowserWindow, Menu, shell, dialog } = require('electron');
const path = require('path');
const { spawn, execSync } = require('child_process');
const http = require('http');
const fs = require('fs');

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const PORT = 8501;
const STREAMLIT_URL = `http://localhost:${PORT}`;
const POLL_INTERVAL_MS = 500;
const MAX_WAIT_MS = 60_000; // 1 minute timeout

// ---------------------------------------------------------------------------
// Dev vs production path resolution
// ---------------------------------------------------------------------------
const isDev = (() => {
  try {
    return require('electron-is-dev');
  } catch {
    return !app.isPackaged;
  }
})();

/**
 * Root directory of the Python/Streamlit project.
 * - Dev:        the repo root (one level up from desktop/)
 * - Production: the extraResources "app" folder inside the .app bundle
 */
const projectRoot = isDev
  ? path.resolve(__dirname, '..')
  : path.join(process.resourcesPath, 'app');

// ---------------------------------------------------------------------------
// Python executable detection
// ---------------------------------------------------------------------------
function findPython() {
  const candidates = [
    path.join(projectRoot, '.venv', 'bin', 'python3'),
    path.join(projectRoot, '.venv', 'bin', 'python'),
    'python3',
    'python',
  ];

  for (const candidate of candidates) {
    try {
      // For absolute paths, check existence; for PATH-based names, probe via execSync
      if (path.isAbsolute(candidate)) {
        if (fs.existsSync(candidate)) return candidate;
      } else {
        execSync(`which ${candidate}`, { stdio: 'ignore' });
        return candidate;
      }
    } catch {
      // not found, try next
    }
  }

  dialog.showErrorBox(
    'Python Not Found',
    'MeetingMind could not locate a Python 3 interpreter.\n\n' +
      'Please install Python 3 or create a virtual environment at ' +
      path.join(projectRoot, '.venv') +
      ' and try again.'
  );
  app.quit();
  return null;
}

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let mainWindow = null;
let splashWindow = null;
let streamlitProc = null;
let pollTimer = null;
let waitedMs = 0;

// ---------------------------------------------------------------------------
// Splash window
// ---------------------------------------------------------------------------
function createSplash() {
  splashWindow = new BrowserWindow({
    width: 480,
    height: 320,
    frame: false,
    resizable: false,
    transparent: false,
    backgroundColor: '#09090F',
    alwaysOnTop: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  splashWindow.loadFile(path.join(__dirname, 'splash.html'));
  splashWindow.center();
}

// ---------------------------------------------------------------------------
// Main window
// ---------------------------------------------------------------------------
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 900,
    minHeight: 600,
    show: false,
    backgroundColor: '#09090F',
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      // Allow the Streamlit iframe/page to function correctly
      webSecurity: false,
    },
    icon: path.join(__dirname, 'icon.png'),
  });

  buildAppMenu();

  mainWindow.on('closed', () => {
    mainWindow = null;
    cleanup();
  });

  // Open external links in the system browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

// ---------------------------------------------------------------------------
// App menu
// ---------------------------------------------------------------------------
function buildAppMenu() {
  const isMac = process.platform === 'darwin';

  const template = [
    // macOS application menu
    ...(isMac
      ? [
          {
            label: app.name,
            submenu: [
              {
                label: 'About MeetingMind',
                click: showAbout,
              },
              { type: 'separator' },
              { role: 'services' },
              { type: 'separator' },
              { role: 'hide' },
              { role: 'hideOthers' },
              { role: 'unhide' },
              { type: 'separator' },
              { role: 'quit' },
            ],
          },
        ]
      : []),

    // File
    {
      label: 'File',
      submenu: [
        isMac ? { role: 'close' } : { role: 'quit', label: 'Quit MeetingMind' },
      ],
    },

    // Edit (standard)
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' },
      ],
    },

    // View
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        {
          label: 'Toggle Developer Tools',
          accelerator: isMac ? 'Alt+Cmd+I' : 'Ctrl+Shift+I',
          click: () => {
            if (mainWindow) mainWindow.webContents.toggleDevTools();
          },
        },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },

    // Window
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'zoom' },
        ...(isMac
          ? [{ type: 'separator' }, { role: 'front' }]
          : [{ role: 'close' }]),
      ],
    },

    // Help
    {
      role: 'help',
      submenu: [
        {
          label: 'About MeetingMind',
          click: showAbout,
        },
        {
          label: 'Open Project on GitHub',
          click: () => shell.openExternal('https://github.com/naityapatel/ai-meeting-notes'),
        },
      ],
    },
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

function showAbout() {
  dialog.showMessageBox(mainWindow || undefined, {
    type: 'info',
    title: 'About MeetingMind',
    message: 'MeetingMind',
    detail:
      'Version 2.0.0\n' +
      'Edge-Native AI Meeting Intelligence Platform\n\n' +
      'Transcribe, summarise, and act on meetings — entirely on-device.',
    buttons: ['OK'],
    icon: path.join(__dirname, 'icon.png'),
  });
}

// ---------------------------------------------------------------------------
// Streamlit server lifecycle
// ---------------------------------------------------------------------------
function startStreamlit(pythonBin) {
  const args = [
    '-m',
    'streamlit',
    'run',
    path.join(projectRoot, 'app.py'),
    '--server.headless',
    'true',
    '--server.port',
    String(PORT),
    '--server.enableCORS',
    'false',
    '--server.enableXsrfProtection',
    'false',
  ];

  console.log(`[MeetingMind] Spawning: ${pythonBin} ${args.join(' ')}`);
  console.log(`[MeetingMind] CWD: ${projectRoot}`);

  streamlitProc = spawn(pythonBin, args, {
    cwd: projectRoot,
    env: { ...process.env, PYTHONUNBUFFERED: '1' },
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  streamlitProc.stdout.on('data', (d) =>
    console.log('[streamlit]', d.toString().trim())
  );
  streamlitProc.stderr.on('data', (d) =>
    console.error('[streamlit:err]', d.toString().trim())
  );

  streamlitProc.on('exit', (code, signal) => {
    console.log(`[MeetingMind] Streamlit exited — code=${code} signal=${signal}`);
    streamlitProc = null;
    // If the main window is still open the server died unexpectedly
    if (mainWindow && !mainWindow.isDestroyed()) {
      dialog.showErrorBox(
        'AI Engine Stopped',
        'The Streamlit server stopped unexpectedly.\n\n' +
          'Please restart MeetingMind.'
      );
      app.quit();
    }
  });
}

// ---------------------------------------------------------------------------
// Readiness polling
// ---------------------------------------------------------------------------
function pollForReady(onReady) {
  waitedMs = 0;

  const check = () => {
    const req = http.get(STREAMLIT_URL, (res) => {
      if (res.statusCode === 200 || res.statusCode === 302) {
        clearTimeout(pollTimer);
        onReady();
      } else {
        scheduleNext();
      }
      res.resume(); // consume response body
    });

    req.on('error', scheduleNext);
    req.setTimeout(POLL_INTERVAL_MS, () => {
      req.destroy();
      scheduleNext();
    });
  };

  const scheduleNext = () => {
    waitedMs += POLL_INTERVAL_MS;
    if (waitedMs >= MAX_WAIT_MS) {
      dialog.showErrorBox(
        'Startup Timeout',
        `MeetingMind's AI engine did not start within ${MAX_WAIT_MS / 1000} seconds.\n\n` +
          'Check that all Python dependencies are installed:\n\n' +
          `  cd "${projectRoot}"\n  pip install -r requirements.txt`
      );
      app.quit();
      return;
    }
    pollTimer = setTimeout(check, POLL_INTERVAL_MS);
  };

  check();
}

// ---------------------------------------------------------------------------
// Cleanup
// ---------------------------------------------------------------------------
function cleanup() {
  if (pollTimer) {
    clearTimeout(pollTimer);
    pollTimer = null;
  }

  if (streamlitProc) {
    console.log('[MeetingMind] Killing Streamlit process...');
    try {
      // Kill the whole process group so child processes (whisper, etc.) are also terminated
      process.kill(-streamlitProc.pid, 'SIGTERM');
    } catch {
      streamlitProc.kill('SIGTERM');
    }
    streamlitProc = null;
  }
}

// ---------------------------------------------------------------------------
// App lifecycle
// ---------------------------------------------------------------------------
app.whenReady().then(() => {
  const pythonBin = findPython();
  if (!pythonBin) return;

  createSplash();
  createMainWindow();
  startStreamlit(pythonBin);

  pollForReady(() => {
    console.log('[MeetingMind] Streamlit is ready — opening main window');

    mainWindow.loadURL(STREAMLIT_URL);

    mainWindow.once('ready-to-show', () => {
      if (splashWindow && !splashWindow.isDestroyed()) {
        splashWindow.close();
        splashWindow = null;
      }
      mainWindow.show();
      mainWindow.focus();
    });
  });
});

app.on('window-all-closed', () => {
  cleanup();
  // On macOS apps conventionally stay active until Cmd+Q
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  // macOS: re-open window when dock icon is clicked
  if (BrowserWindow.getAllWindows().length === 0) {
    createMainWindow();
    if (mainWindow) mainWindow.loadURL(STREAMLIT_URL);
  }
});

app.on('before-quit', cleanup);

// Prevent navigation away from the Streamlit app
app.on('web-contents-created', (_event, contents) => {
  contents.on('will-navigate', (event, url) => {
    if (!url.startsWith(STREAMLIT_URL)) {
      event.preventDefault();
      shell.openExternal(url);
    }
  });
});
