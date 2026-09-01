"""Persist interactive `chat` history as JSON under XDG state.

Kept deliberately small: one JSON array of OpenAI-style message dicts at
``~/.local/state/local-ai-assistant/chat-history.json``. The array always starts
with the system prompt so a resumed session behaves like a fresh one.
"""

import json
from pathlib import Path

from .config import CHAT_HISTORY_FILE

SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are a concise, helpful local assistant running on an AMD NPU.",
}


def _fresh() -> list[dict]:
    return [dict(SYSTEM_PROMPT)]


def load_history(path: Path = CHAT_HISTORY_FILE) -> list[dict]:
    """Return the saved message list, or a fresh one if absent/unreadable."""
    try:
        data = json.loads(path.read_text())
    except (FileNotFoundError, ValueError):
        return _fresh()
    if not isinstance(data, list) or not data:
        return _fresh()
    return data


def save_history(history: list[dict], path: Path = CHAT_HISTORY_FILE) -> None:
    """Write the message list to disk, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, indent=2))


def clear_history(path: Path = CHAT_HISTORY_FILE) -> None:
    """Delete the saved history file if it exists."""
    path.unlink(missing_ok=True)
