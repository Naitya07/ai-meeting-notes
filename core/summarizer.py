"""
MeetingMind - Summarizer
Generates structured meeting notes from transcript using Ollama (llama3.2).
"""

import json
import re
import requests
from typing import Optional, Callable

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"

# Max characters to send to the model (avoid context overflow)
MAX_TRANSCRIPT_CHARS = 12000


def _call_ollama(prompt: str, model: str = DEFAULT_MODEL, stream: bool = False) -> str:
    """
    Call Ollama API and return the generated text.
    Raises ConnectionError if Ollama is not running.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 2048,
        }
    }

    try:
        if stream:
            # Stream and collect
            response = requests.post(url, json=payload, stream=True, timeout=180)
            response.raise_for_status()
            full_text = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    full_text += chunk.get("response", "")
                    if chunk.get("done"):
                        break
            return full_text.strip()
        else:
            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Cannot connect to Ollama. Please ensure Ollama is running: `ollama serve`"
        )
    except requests.exceptions.Timeout:
        raise TimeoutError("Ollama request timed out. The transcript may be too long.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ollama API error: {e}")


def check_ollama_available(model: str = DEFAULT_MODEL) -> tuple[bool, str]:
    """
    Check if Ollama is running and the model is available.
    Returns (available: bool, message: str).
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            return False, "Ollama is running but returned an unexpected response."

        data = response.json()
        models = [m["name"] for m in data.get("models", [])]

        # Check exact or prefix match
        model_available = any(
            m == model or m.startswith(model.split(":")[0])
            for m in models
        )

        if not model_available:
            available_list = ", ".join(models) if models else "none"
            return False, (
                f"Model '{model}' not found. Available: {available_list}. "
                f"Run: `ollama pull {model}`"
            )

        return True, f"Ollama ready with model '{model}'"

    except requests.exceptions.ConnectionError:
        return False, (
            "Ollama is not running. Start it with: `ollama serve`\n"
            "Then pull the model: `ollama pull llama3.2`"
        )
    except Exception as e:
        return False, f"Error checking Ollama: {e}"


def _truncate_transcript(transcript: str, max_chars: int = MAX_TRANSCRIPT_CHARS) -> str:
    """Truncate transcript if too long, keeping beginning and end."""
    if len(transcript) <= max_chars:
        return transcript

    half = max_chars // 2
    beginning = transcript[:half]
    ending = transcript[-half:]
    omitted = len(transcript) - max_chars
    return (
        f"{beginning}\n\n"
        f"[... {omitted:,} characters omitted for brevity ...]\n\n"
        f"{ending}"
    )


def generate_meeting_notes(
    transcript: str,
    meeting_title: str = "Meeting",
    model: str = DEFAULT_MODEL,
    progress_callback: Optional[Callable[[str, float], None]] = None,
) -> dict:
    """
    Generate structured meeting notes from a transcript.

    Returns:
        {
            "summary": list[str],             # 3-5 bullet points
            "key_decisions": list[str],
            "action_items": list[dict],        # {task, assignee, deadline}
            "discussion_topics": list[str],
            "follow_up_items": list[str],
            "meeting_type": str,
            "sentiment": str,
            "raw_response": str,
        }
    """
    if not transcript or not transcript.strip():
        raise ValueError("Transcript is empty.")

    truncated = _truncate_transcript(transcript)

    if progress_callback:
        progress_callback("Analyzing transcript with AI...", 0.1)

    prompt = f"""You are an expert meeting analyst. Analyze the following meeting transcript and extract structured information.

Meeting Title: {meeting_title}

TRANSCRIPT:
{truncated}

Please provide a comprehensive analysis in the following EXACT JSON format. Be specific and extract real information from the transcript:

{{
  "summary": [
    "bullet point 1 (key theme or outcome)",
    "bullet point 2",
    "bullet point 3",
    "bullet point 4 (optional)",
    "bullet point 5 (optional)"
  ],
  "key_decisions": [
    "Decision made during the meeting",
    "Another decision"
  ],
  "action_items": [
    {{
      "task": "Specific action to be taken",
      "assignee": "Person responsible (or 'TBD' if not mentioned)",
      "deadline": "When it should be done (or 'Not specified')",
      "priority": "High/Medium/Low"
    }}
  ],
  "discussion_topics": [
    "Topic 1 that was discussed",
    "Topic 2",
    "Topic 3"
  ],
  "follow_up_items": [
    "Item that needs follow-up",
    "Another follow-up"
  ],
  "meeting_type": "One of: Planning / Status Update / Brainstorm / Review / Decision / Interview / Training / Other",
  "sentiment": "One of: Productive / Challenging / Neutral / Positive / Tense"
}}

IMPORTANT:
- Return ONLY valid JSON, no other text before or after
- Be specific - use actual names, dates, topics from the transcript
- If something is not mentioned, use empty arrays [] or 'Not specified'
- action_items should reflect actual tasks discussed, not generic placeholders
- summary bullets should be complete sentences capturing the key points
"""

    if progress_callback:
        progress_callback("AI is generating meeting notes...", 0.3)

    raw_response = _call_ollama(prompt, model=model, stream=True)

    if progress_callback:
        progress_callback("Parsing AI response...", 0.85)

    # Parse JSON from response
    parsed = _parse_json_response(raw_response)

    if progress_callback:
        progress_callback("Meeting notes ready!", 1.0)

    parsed["raw_response"] = raw_response
    return parsed


def _parse_json_response(response: str) -> dict:
    """
    Robustly parse JSON from model response.
    Handles cases where the model adds extra text around the JSON.
    """
    # Try direct parse first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON block from markdown code fences
    json_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", response)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find the first { ... } block
    brace_match = re.search(r"\{[\s\S]+\}", response)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    # If all parsing fails, return a structured fallback
    return {
        "summary": [
            "AI analysis completed but response format was unexpected.",
            "Please review the raw transcript below for meeting details.",
        ],
        "key_decisions": ["Unable to parse — see raw response"],
        "action_items": [],
        "discussion_topics": ["See full transcript"],
        "follow_up_items": [],
        "meeting_type": "Other",
        "sentiment": "Neutral",
    }


def generate_section(
    transcript: str,
    section: str,
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Regenerate a single section of meeting notes.
    section: "summary" | "action_items" | "key_decisions" | "follow_up_items"
    """
    truncated = _truncate_transcript(transcript)

    section_prompts = {
        "summary": (
            "Provide a meeting summary as 4-5 concise bullet points. "
            "Each bullet should be a complete sentence. Return only the bullets, one per line, starting with '•'."
        ),
        "action_items": (
            "List all action items from the meeting. Format each as:\n"
            "• [Task] — Assignee: [Name or TBD] — Deadline: [Date or Not specified]\n"
            "Return only the action items."
        ),
        "key_decisions": (
            "List all key decisions made in the meeting. "
            "Return each decision as a bullet starting with '•'."
        ),
        "follow_up_items": (
            "List all follow-up items that need attention after this meeting. "
            "Return each as a bullet starting with '•'."
        ),
    }

    instruction = section_prompts.get(
        section,
        f"Summarize the '{section}' aspect of this meeting."
    )

    prompt = f"""Analyze this meeting transcript and {instruction}

TRANSCRIPT:
{truncated}"""

    return _call_ollama(prompt, model=model, stream=True)
