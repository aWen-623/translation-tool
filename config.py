"""Configuration management — env vars + persistent settings.json."""

import json
import os
from dotenv import load_dotenv

load_dotenv()

# ── API credentials (from .env) ──
BAIDU_APP_ID = os.getenv("BAIDU_APP_ID", "")
BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY", "")
TENCENT_SECRET_ID = os.getenv("TENCENT_SECRET_ID", "")
TENCENT_SECRET_KEY = os.getenv("TENCENT_SECRET_KEY", "")

# ── Paths ──
_BASE = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(_BASE, "history.json")
SETTINGS_FILE = os.path.join(_BASE, "settings.json")

# ── Defaults ──
_DEFAULTS = {
    "hotkey": "ctrl+alt+t",
    "auto_copy": False,
    "source": "auto",
}

# ── Runtime settings ──
_settings: dict = {}


def _load() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return {**_DEFAULTS, **json.load(f)}
        except (json.JSONDecodeError, IOError):
            pass
    return dict(_DEFAULTS)


def _save(data: dict) -> None:
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError:
        pass


def init():
    global _settings
    _settings = _load()


def get(key: str):
    return _settings.get(key, _DEFAULTS.get(key))


def set(key: str, value):
    _settings[key] = value
    _save(_settings)


# ── Window constants ──
MAX_HISTORY = 10
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
