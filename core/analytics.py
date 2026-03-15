"""
MeetingMind - Analytics Engine
Provides insights and statistics across all stored meetings.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from core.storage import _load_index, load_meeting


# ---------------------------------------------------------------------------
# Stop words to exclude from word-cloud generation
# ---------------------------------------------------------------------------
_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "through", "during",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "shall", "can", "need", "dare", "ought", "used", "it", "its", "it's",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
    "your", "yours", "he", "him", "his", "she", "her", "hers", "they",
    "them", "their", "theirs", "what", "which", "who", "whom", "this",
    "that", "these", "those", "am", "not", "no", "so", "if", "then",
    "than", "too", "very", "just", "more", "also", "as", "all", "any",
    "each", "both", "few", "other", "some", "such", "only", "own", "same",
    "how", "when", "where", "why", "s", "t", "re", "ll", "ve", "d", "m",
    "ok", "uh", "um", "yeah", "like", "know", "think", "going", "get",
    "go", "got", "well", "right", "good", "now", "one", "two", "three",
}


class MeetingAnalytics:
    """
    Aggregates metrics and insights across all stored MeetingMind meetings.

    Usage::

        analytics = MeetingAnalytics()
        stats = analytics.get_dashboard_stats()
    """

    def __init__(self):
        """Load the meeting index from storage on construction."""
        self._index: list[dict] = _load_index()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _iter_full_meetings(self):
        """Yield fully-loaded meeting dicts (skips any that fail to load)."""
        for entry in self._index:
            meeting = load_meeting(entry["id"])
            if meeting:
                yield meeting

    def _parse_dt(self, iso_str: str) -> Optional[datetime]:
        """Parse an ISO-8601 timestamp, returning None on failure."""
        if not iso_str:
            return None
        try:
            # Python 3.7+ fromisoformat doesn't handle the trailing Z
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            # Normalise to UTC-aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            return None

    def _get_action_items(self, meeting: dict) -> list[dict]:
        """Return normalised action items from a meeting's notes."""
        raw = meeting.get("notes", {}).get("action_items", [])
        normalised = []
        for item in raw:
            if isinstance(item, dict):
                normalised.append(item)
            elif isinstance(item, str):
                normalised.append({"task": item, "priority": "Medium", "assignee": ""})
        return normalised

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_dashboard_stats(self) -> dict:
        """
        Return a summary dict suitable for a dashboard header.

        Keys: total_meetings, total_duration_hours, total_words,
              avg_duration_minutes, avg_words_per_meeting,
              meetings_this_week, meetings_this_month,
              most_common_type, most_common_sentiment, streak_days.
        """
        now = datetime.now(tz=timezone.utc)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        total_meetings = len(self._index)
        total_duration_seconds = 0.0
        total_words = 0
        meetings_this_week = 0
        meetings_this_month = 0
        types: list[str] = []
        sentiments: list[str] = []
        meeting_dates: set[str] = set()

        for entry in self._index:
            total_duration_seconds += float(entry.get("duration", 0) or 0)
            total_words += int(entry.get("word_count", 0) or 0)

            types.append(entry.get("meeting_type", "Other") or "Other")
            sentiments.append(entry.get("sentiment", "Neutral") or "Neutral")

            dt = self._parse_dt(entry.get("created_at"))
            if dt:
                if dt >= week_ago:
                    meetings_this_week += 1
                if dt >= month_ago:
                    meetings_this_month += 1
                meeting_dates.add(dt.strftime("%Y-%m-%d"))

        avg_duration_minutes = (
            (total_duration_seconds / 60 / total_meetings) if total_meetings else 0
        )
        avg_words = total_words / total_meetings if total_meetings else 0

        type_counter = Counter(types)
        sentiment_counter = Counter(sentiments)
        most_common_type = type_counter.most_common(1)[0][0] if type_counter else "N/A"
        most_common_sentiment = (
            sentiment_counter.most_common(1)[0][0] if sentiment_counter else "N/A"
        )

        streak = self._calculate_streak(meeting_dates, now)

        return {
            "total_meetings": total_meetings,
            "total_duration_hours": round(total_duration_seconds / 3600, 2),
            "total_words": total_words,
            "avg_duration_minutes": round(avg_duration_minutes, 1),
            "avg_words_per_meeting": round(avg_words),
            "meetings_this_week": meetings_this_week,
            "meetings_this_month": meetings_this_month,
            "most_common_type": most_common_type,
            "most_common_sentiment": most_common_sentiment,
            "streak_days": streak,
        }

    def _calculate_streak(self, meeting_dates: set[str], now: datetime) -> int:
        """Return the number of consecutive days (ending today) that had meetings."""
        streak = 0
        current = now.date()
        while current.strftime("%Y-%m-%d") in meeting_dates:
            streak += 1
            current -= timedelta(days=1)
        return streak

    def get_meeting_trends(self, period: str = "week") -> list[dict]:
        """
        Return per-day meeting counts and total duration for trend charts.

        Args:
            period: "week" (last 7 days), "month" (last 30 days),
                    or "year" (last 365 days).

        Returns:
            List of {date: "YYYY-MM-DD", count: int, total_duration: float}
            sorted oldest-first.
        """
        period_days = {"week": 7, "month": 30, "year": 365}.get(period, 7)
        now = datetime.now(tz=timezone.utc)
        cutoff = now - timedelta(days=period_days)

        # Initialise every day in the range to zero
        day_data: dict[str, dict] = {}
        for i in range(period_days):
            day = (cutoff + timedelta(days=i + 1)).strftime("%Y-%m-%d")
            day_data[day] = {"date": day, "count": 0, "total_duration": 0.0}

        for entry in self._index:
            dt = self._parse_dt(entry.get("created_at"))
            if not dt or dt < cutoff:
                continue
            day_key = dt.strftime("%Y-%m-%d")
            if day_key in day_data:
                day_data[day_key]["count"] += 1
                day_data[day_key]["total_duration"] += float(
                    entry.get("duration", 0) or 0
                )

        return sorted(day_data.values(), key=lambda x: x["date"])

    def get_vertical_distribution(self) -> dict[str, int]:
        """
        Return meeting-count grouped by vertical/category.

        Falls back to "meeting_type" when a dedicated vertical field is absent.
        """
        counter: Counter = Counter()
        for entry in self._index:
            vertical = (
                entry.get("vertical")
                or entry.get("vertical_id")
                or entry.get("meeting_type")
                or "Other"
            )
            counter[vertical] += 1
        return dict(counter)

    def get_sentiment_distribution(self) -> dict[str, int]:
        """Return {sentiment_label: count} across all meetings."""
        counter: Counter = Counter()
        for entry in self._index:
            sentiment = entry.get("sentiment") or "Neutral"
            counter[sentiment] += 1
        return dict(counter)

    def get_meeting_type_distribution(self) -> dict[str, int]:
        """Return {meeting_type: count} across all meetings."""
        counter: Counter = Counter()
        for entry in self._index:
            mtype = entry.get("meeting_type") or "Other"
            counter[mtype] += 1
        return dict(counter)

    def get_action_item_stats(self) -> dict:
        """
        Return aggregated action-item statistics.

        Keys: total, by_priority {High, Medium, Low}, by_assignee {name: count}.
        """
        total = 0
        by_priority: Counter = Counter()
        by_assignee: Counter = Counter()

        for meeting in self._iter_full_meetings():
            for item in self._get_action_items(meeting):
                total += 1
                priority = item.get("priority") or "Medium"
                by_priority[priority] += 1
                assignee = (item.get("assignee") or "").strip()
                if assignee:
                    by_assignee[assignee] += 1

        return {
            "total": total,
            "by_priority": {
                "High": by_priority.get("High", 0),
                "Medium": by_priority.get("Medium", 0),
                "Low": by_priority.get("Low", 0),
            },
            "by_assignee": dict(by_assignee.most_common()),
        }

    def get_language_distribution(self) -> dict[str, int]:
        """Return {language_code: count} across all meetings."""
        counter: Counter = Counter()
        for entry in self._index:
            lang = entry.get("language") or "unknown"
            counter[lang] += 1
        return dict(counter)

    def get_productivity_score(self) -> int:
        """
        Return a 0-100 productivity score.

        Score is weighted across three signals:
        - Action item density  (action items per meeting)   — 40 pts max
        - Decision count       (decisions per meeting)      — 35 pts max
        - Follow-up ratio      (meetings with follow-ups)   — 25 pts max
        """
        if not self._index:
            return 0

        total_meetings = len(self._index)
        total_action_items = 0
        total_decisions = 0
        meetings_with_followups = 0

        for meeting in self._iter_full_meetings():
            notes = meeting.get("notes", {})
            total_action_items += len(self._get_action_items(meeting))
            total_decisions += len(notes.get("decisions", []) or [])
            if notes.get("follow_up_questions") or notes.get("next_steps"):
                meetings_with_followups += 1

        # Density signals normalised to reasonable ceilings
        action_density = total_action_items / total_meetings  # ideal ≈ 5
        decision_density = total_decisions / total_meetings   # ideal ≈ 3
        followup_ratio = meetings_with_followups / total_meetings  # ideal ≈ 0.8

        action_score = min(action_density / 5.0, 1.0) * 40
        decision_score = min(decision_density / 3.0, 1.0) * 35
        followup_score = min(followup_ratio / 0.8, 1.0) * 25

        return round(action_score + decision_score + followup_score)

    def get_word_cloud_data(self, top_n: int = 50) -> list[dict]:
        """
        Return the top_n most frequent content words across all transcripts.

        Returns: list of {word: str, count: int}, sorted by count descending.
        """
        counter: Counter = Counter()
        word_re = re.compile(r"[a-z]{3,}")  # at least 3 chars, alpha only

        for meeting in self._iter_full_meetings():
            transcript = meeting.get("transcript", "") or ""
            for word in word_re.findall(transcript.lower()):
                if word not in _STOP_WORDS:
                    counter[word] += 1

        return [
            {"word": word, "count": count}
            for word, count in counter.most_common(top_n)
        ]

    def get_peak_meeting_hours(self) -> dict[int, int]:
        """
        Return {hour: count} for hours 0-23 based on meeting start times.
        """
        hour_counts: dict[int, int] = {h: 0 for h in range(24)}
        for entry in self._index:
            dt = self._parse_dt(entry.get("created_at"))
            if dt:
                # Convert to local time for meaningful "hour of day"
                local_dt = dt.astimezone()
                hour_counts[local_dt.hour] += 1
        return hour_counts

    def get_duration_histogram(self) -> list[dict]:
        """
        Return meeting-count bucketed into duration ranges.

        Buckets: 0-15 min, 15-30 min, 30-60 min, 60-90 min, 90+ min.
        """
        buckets = [
            {"range": "0-15min",   "min": 0,    "max": 15,   "count": 0},
            {"range": "15-30min",  "min": 15,   "max": 30,   "count": 0},
            {"range": "30-60min",  "min": 30,   "max": 60,   "count": 0},
            {"range": "60-90min",  "min": 60,   "max": 90,   "count": 0},
            {"range": "90+min",    "min": 90,   "max": None,  "count": 0},
        ]

        for entry in self._index:
            duration_minutes = float(entry.get("duration", 0) or 0) / 60
            for bucket in buckets:
                if bucket["max"] is None:
                    if duration_minutes >= bucket["min"]:
                        bucket["count"] += 1
                        break
                elif bucket["min"] <= duration_minutes < bucket["max"]:
                    bucket["count"] += 1
                    break

        # Return without internal min/max keys — just range + count
        return [{"range": b["range"], "count": b["count"]} for b in buckets]


# ---------------------------------------------------------------------------
# Module-level helper functions
# ---------------------------------------------------------------------------

def calculate_speaking_pace(word_count: int, duration_seconds: float) -> float:
    """
    Return speaking pace in words per minute.

    Args:
        word_count:        Total words in the transcript.
        duration_seconds:  Meeting duration in seconds.

    Returns:
        Words per minute as a float, or 0.0 if duration is zero.
    """
    if not duration_seconds or duration_seconds <= 0:
        return 0.0
    duration_minutes = duration_seconds / 60
    return round(word_count / duration_minutes, 1)


def estimate_time_saved(word_count: int) -> dict:
    """
    Estimate the manual note-taking time saved by AI transcription.

    Assumes a human typist averages 40 WPM when taking notes from memory,
    compared to near-instant AI processing.

    Args:
        word_count: Total words transcribed.

    Returns:
        Dict with keys: manual_minutes, ai_seconds, saved_minutes.
    """
    typing_wpm = 40
    manual_minutes = round(word_count / typing_wpm, 1)
    # AI transcription time approximated as 10% of audio duration at ~130 WPM
    # but for the purposes of this estimate we use near-zero (< 1 s per 100 words)
    ai_seconds = round(word_count / 100 * 0.8, 1)
    saved_minutes = round(manual_minutes - ai_seconds / 60, 1)

    return {
        "manual_minutes": manual_minutes,
        "ai_seconds": ai_seconds,
        "saved_minutes": max(saved_minutes, 0.0),
    }


def format_insight(stat_name: str, value) -> str:
    """
    Return a human-readable insight string for a given stat.

    Args:
        stat_name: One of the known dashboard stat keys.
        value:     The numeric or string value of the stat.

    Returns:
        A plain-English sentence describing the stat.
    """
    templates: dict[str, str] = {
        "total_meetings":         "You have recorded {value} meeting{s} in total.",
        "total_duration_hours":   "Your meetings have totalled {value} hours of audio.",
        "total_words":            "{value:,} words have been transcribed across all meetings.",
        "avg_duration_minutes":   "Your average meeting lasts {value} minutes.",
        "avg_words_per_meeting":  "Meetings average {value:,} words of discussion.",
        "meetings_this_week":     "You have had {value} meeting{s} in the last 7 days.",
        "meetings_this_month":    "You have had {value} meeting{s} in the last 30 days.",
        "most_common_type":       "Your most common meeting type is {value}.",
        "most_common_sentiment":  "The most frequent meeting sentiment is {value}.",
        "streak_days":            "You have a {value}-day meeting streak — keep it up!",
    }

    template = templates.get(stat_name)
    if not template:
        return f"{stat_name}: {value}"

    # Pluralise where needed
    try:
        plural = "s" if int(value) != 1 else ""
    except (TypeError, ValueError):
        plural = "s"

    try:
        return template.format(value=value, s=plural)
    except (KeyError, ValueError):
        return f"{stat_name}: {value}"
