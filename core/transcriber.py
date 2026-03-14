"""
MeetingMind - Transcriber
Handles audio extraction from video files and Whisper transcription.
"""

import os
import sys
import tempfile
import subprocess
import time
from pathlib import Path
from typing import Callable, Optional

# Ensure ~/bin is in PATH for ffmpeg
HOME_BIN = str(Path.home() / "bin")
if HOME_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = HOME_BIN + ":" + os.environ.get("PATH", "")


def extract_audio(input_path: str, output_path: str) -> bool:
    """
    Extract audio from video file using ffmpeg.
    Returns True on success, False on failure.
    """
    ffmpeg_bin = str(Path.home() / "bin" / "ffmpeg")
    if not os.path.exists(ffmpeg_bin):
        # Fall back to system ffmpeg
        ffmpeg_bin = "ffmpeg"

    cmd = [
        ffmpeg_bin,
        "-i", input_path,
        "-vn",                     # No video
        "-acodec", "pcm_s16le",   # WAV PCM 16-bit
        "-ar", "16000",            # 16kHz sample rate (Whisper optimal)
        "-ac", "1",                # Mono
        "-y",                      # Overwrite
        output_path
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def transcribe_audio(
    file_path: str,
    model_name: str = "base",
    progress_callback: Optional[Callable[[str, float], None]] = None,
    language: Optional[str] = None,
) -> dict:
    """
    Transcribe an audio/video file using OpenAI Whisper.

    Args:
        file_path: Path to the audio/video file
        model_name: Whisper model size ("tiny", "base", "small", "medium", "large")
        progress_callback: Optional callback(message, progress_0_to_1)
        language: Optional language code (e.g. "en"). None = auto-detect.

    Returns:
        {
            "text": full transcript string,
            "segments": [{"start": float, "end": float, "text": str}, ...],
            "language": str,
            "duration": float,
            "word_count": int,
            "formatted_transcript": str  (with timestamps),
        }
    """
    import whisper

    suffix = Path(file_path).suffix.lower()
    video_extensions = {".mp4", ".mov", ".webm", ".mkv", ".avi"}

    audio_path = file_path
    tmp_audio = None

    # Extract audio from video files
    if suffix in video_extensions:
        if progress_callback:
            progress_callback("Extracting audio from video...", 0.05)

        tmp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_audio.close()

        success = extract_audio(file_path, tmp_audio.name)
        if not success:
            # Try imageio-ffmpeg as fallback
            try:
                import imageio_ffmpeg as iio_ffmpeg
                ffmpeg_exe = iio_ffmpeg.get_ffmpeg_exe()
                cmd = [
                    ffmpeg_exe,
                    "-i", file_path,
                    "-vn", "-acodec", "pcm_s16le",
                    "-ar", "16000", "-ac", "1", "-y",
                    tmp_audio.name
                ]
                subprocess.run(cmd, capture_output=True, timeout=300)
            except Exception:
                pass

        audio_path = tmp_audio.name

    try:
        if progress_callback:
            progress_callback(f"Loading Whisper '{model_name}' model...", 0.1)

        model = whisper.load_model(model_name)

        if progress_callback:
            progress_callback("Transcribing audio... (this may take a while)", 0.2)

        # Run transcription
        transcribe_kwargs = {
            "verbose": False,
            "word_timestamps": False,
        }
        if language:
            transcribe_kwargs["language"] = language

        result = model.transcribe(audio_path, **transcribe_kwargs)

        if progress_callback:
            progress_callback("Processing transcript...", 0.9)

        segments = result.get("segments", [])
        full_text = result.get("text", "").strip()
        detected_language = result.get("language", "en")

        # Build formatted transcript with timestamps
        formatted_lines = []
        for seg in segments:
            start_ts = format_timestamp(seg["start"])
            end_ts = format_timestamp(seg["end"])
            text = seg["text"].strip()
            if text:
                formatted_lines.append(f"[{start_ts} → {end_ts}]  {text}")

        formatted_transcript = "\n".join(formatted_lines)

        # Calculate duration
        duration = segments[-1]["end"] if segments else 0.0

        if progress_callback:
            progress_callback("Transcription complete!", 1.0)

        return {
            "text": full_text,
            "segments": segments,
            "language": detected_language,
            "duration": duration,
            "word_count": len(full_text.split()),
            "formatted_transcript": formatted_transcript,
        }

    finally:
        # Clean up temp audio file
        if tmp_audio and os.path.exists(tmp_audio.name):
            try:
                os.unlink(tmp_audio.name)
            except OSError:
                pass


def apply_speaker_labels(
    segments: list,
    speaker_map: dict,
    num_speakers: int = 2,
) -> str:
    """
    Apply speaker labels to transcript segments by distributing them evenly
    (since we don't have diarization). Returns formatted transcript.

    Args:
        segments: Whisper segment list
        speaker_map: {speaker_index: "Name"} e.g. {0: "Alice", 1: "Bob"}
        num_speakers: Total number of speakers
    """
    if not segments or not speaker_map or num_speakers < 1:
        lines = []
        for seg in segments:
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = seg["text"].strip()
            if text:
                lines.append(f"[{start} → {end}]  {text}")
        return "\n".join(lines)

    # Simple heuristic: detect speaker change by pause length
    lines = []
    current_speaker_idx = 0
    prev_end = 0.0
    PAUSE_THRESHOLD = 1.5  # seconds gap = likely speaker change

    for i, seg in enumerate(segments):
        start = seg["start"]
        end = seg["end"]
        text = seg["text"].strip()
        if not text:
            continue

        # Detect pause suggesting speaker switch
        if i > 0 and (start - prev_end) > PAUSE_THRESHOLD:
            current_speaker_idx = (current_speaker_idx + 1) % num_speakers

        speaker_name = speaker_map.get(current_speaker_idx, f"Speaker {current_speaker_idx + 1}")
        start_ts = format_timestamp(start)
        end_ts = format_timestamp(end)
        lines.append(f"[{start_ts} → {end_ts}]  **{speaker_name}:** {text}")
        prev_end = end

    return "\n".join(lines)
