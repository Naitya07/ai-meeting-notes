"""
MeetingMind - Storage
Handles saving, loading, and searching meeting history in ~/.meetingmind/
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid


STORAGE_DIR = Path.home() / ".meetingmind"
MEETINGS_DIR = STORAGE_DIR / "meetings"
INDEX_FILE = STORAGE_DIR / "index.json"


def _ensure_dirs():
    """Create storage directories if they don't exist."""
    MEETINGS_DIR.mkdir(parents=True, exist_ok=True)


def _load_index() -> list:
    """Load the meetings index file."""
    if not INDEX_FILE.exists():
        return []
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_index(index: list):
    """Save the meetings index file."""
    _ensure_dirs()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def save_meeting(
    title: str,
    transcript: str,
    notes: dict,
    file_name: str,
    duration: float,
    language: str,
    word_count: int,
    formatted_transcript: str,
    segments: list,
    audio_path: Optional[str] = None,
) -> str:
    """
    Save a meeting to persistent storage.

    Returns the meeting_id string.
    """
    _ensure_dirs()

    meeting_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    meeting_data = {
        "id": meeting_id,
        "title": title,
        "created_at": timestamp,
        "updated_at": timestamp,
        "file_name": file_name,
        "duration": duration,
        "language": language,
        "word_count": word_count,
        "transcript": transcript,
        "formatted_transcript": formatted_transcript,
        "segments": segments,
        "notes": notes,
        "audio_path": audio_path,
    }

    # Save individual meeting file
    meeting_file = MEETINGS_DIR / f"{meeting_id}.json"
    with open(meeting_file, "w", encoding="utf-8") as f:
        json.dump(meeting_data, f, indent=2, ensure_ascii=False)

    # Update index
    index = _load_index()
    index_entry = {
        "id": meeting_id,
        "title": title,
        "created_at": timestamp,
        "file_name": file_name,
        "duration": duration,
        "language": language,
        "word_count": word_count,
        "meeting_type": notes.get("meeting_type", "Other"),
        "sentiment": notes.get("sentiment", "Neutral"),
        "summary_preview": (
            notes.get("summary", [""])[0][:120] + "..."
            if notes.get("summary")
            else ""
        ),
    }

    # Remove existing entry if re-saving same ID
    index = [m for m in index if m["id"] != meeting_id]
    index.insert(0, index_entry)  # Most recent first
    _save_index(index)

    return meeting_id


def load_meeting(meeting_id: str) -> Optional[dict]:
    """Load a full meeting record by ID. Returns None if not found."""
    meeting_file = MEETINGS_DIR / f"{meeting_id}.json"
    if not meeting_file.exists():
        return None
    try:
        with open(meeting_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def list_meetings() -> list:
    """
    Return list of meeting index entries, most recent first.
    Each entry: {id, title, created_at, file_name, duration, word_count, meeting_type, sentiment, summary_preview}
    """
    return _load_index()


def delete_meeting(meeting_id: str) -> bool:
    """Delete a meeting by ID. Returns True on success."""
    meeting_file = MEETINGS_DIR / f"{meeting_id}.json"
    deleted = False

    if meeting_file.exists():
        meeting_file.unlink()
        deleted = True

    # Remove from index
    index = _load_index()
    new_index = [m for m in index if m["id"] != meeting_id]
    if len(new_index) != len(index):
        _save_index(new_index)
        deleted = True

    return deleted


def update_meeting_title(meeting_id: str, new_title: str) -> bool:
    """Update just the title of an existing meeting."""
    meeting = load_meeting(meeting_id)
    if not meeting:
        return False

    meeting["title"] = new_title
    meeting["updated_at"] = datetime.now().isoformat()

    meeting_file = MEETINGS_DIR / f"{meeting_id}.json"
    with open(meeting_file, "w", encoding="utf-8") as f:
        json.dump(meeting, f, indent=2, ensure_ascii=False)

    # Update index
    index = _load_index()
    for entry in index:
        if entry["id"] == meeting_id:
            entry["title"] = new_title
            break
    _save_index(index)
    return True


def search_meetings(query: str) -> list:
    """
    Search across all meeting transcripts and notes.
    Returns list of {id, title, created_at, matches: [str]} dicts.
    """
    if not query or not query.strip():
        return list_meetings()

    query_lower = query.strip().lower()
    results = []

    for entry in _load_index():
        meeting = load_meeting(entry["id"])
        if not meeting:
            continue

        matches = []
        score = 0

        # Search in title
        if query_lower in meeting.get("title", "").lower():
            score += 10
            matches.append(f"Title: {meeting['title']}")

        # Search in transcript
        transcript = meeting.get("transcript", "").lower()
        if query_lower in transcript:
            # Find context around match
            idx = transcript.find(query_lower)
            start = max(0, idx - 60)
            end = min(len(transcript), idx + 100)
            snippet = meeting.get("transcript", "")[start:end].replace("\n", " ").strip()
            matches.append(f"Transcript: ...{snippet}...")
            score += 5

        # Search in notes
        notes = meeting.get("notes", {})

        for bullet in notes.get("summary", []):
            if query_lower in bullet.lower():
                matches.append(f"Summary: {bullet[:120]}")
                score += 3

        for item in notes.get("action_items", []):
            task = item.get("task", "") if isinstance(item, dict) else str(item)
            if query_lower in task.lower():
                matches.append(f"Action item: {task[:120]}")
                score += 3

        for topic in notes.get("discussion_topics", []):
            if query_lower in topic.lower():
                matches.append(f"Topic: {topic[:120]}")
                score += 2

        if score > 0:
            result = {**entry, "matches": matches[:3], "score": score}
            results.append(result)

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def get_storage_stats() -> dict:
    """Return storage usage statistics."""
    index = _load_index()
    total_size = 0

    if MEETINGS_DIR.exists():
        for f in MEETINGS_DIR.glob("*.json"):
            total_size += f.stat().st_size

    return {
        "total_meetings": len(index),
        "storage_path": str(STORAGE_DIR),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
    }


def export_all_meetings_json() -> str:
    """Export all meeting data as a single JSON string."""
    all_meetings = []
    for entry in _load_index():
        meeting = load_meeting(entry["id"])
        if meeting:
            all_meetings.append(meeting)

    return json.dumps(all_meetings, indent=2, ensure_ascii=False)
