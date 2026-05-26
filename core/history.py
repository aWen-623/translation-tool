"""Translation history — stores up to MAX_HISTORY entries."""

import json
import os
from datetime import datetime

import config


def _load() -> list:
    if not os.path.exists(config.HISTORY_FILE):
        return []
    try:
        with open(config.HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError, OSError):
        return []


def _save(history: list) -> None:
    try:
        with open(config.HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[:config.MAX_HISTORY], f, ensure_ascii=False, indent=2)
    except (IOError, OSError):
        pass


def add(source_text: str, translated_text: str, source_lang: str, target_lang: str) -> None:
    if not source_text.strip() or not translated_text.strip():
        return
    history = _load()
    # Skip exact duplicate at top
    if history and history[0].get("source") == source_text and history[0].get("to") == target_lang:
        return
    entry = {
        "source": source_text,
        "translated": translated_text,
        "from": source_lang,
        "to": target_lang,
        "time": datetime.now().strftime("%m-%d %H:%M"),
    }
    history.insert(0, entry)
    _save(history)


def get_all() -> list:
    return _load()


def clear() -> None:
    _save([])
