"""Language definitions, detection, and API code mapping."""

import re

# ── Language definitions ──
LANGUAGES = {
    "auto": {"name": "自动检测", "baidu": "auto", "tencent": "auto"},
    "zh":   {"name": "中文",     "baidu": "zh",  "tencent": "zh"},
    "en":   {"name": "英语",     "baidu": "en",  "tencent": "en"},
    "ja":   {"name": "日语",     "baidu": "jp",  "tencent": "ja"},
    "ko":   {"name": "韩语",     "baidu": "kor", "tencent": "ko"},
    "ru":   {"name": "俄语",     "baidu": "ru",  "tencent": "ru"},
    "cht":  {"name": "繁体中文", "baidu": "cht", "tencent": "zh-TW"},
}

# Source languages (exclude auto for manual selection)
SOURCE_LANGS = ["zh", "en", "ja", "ko", "ru"]

# Target languages (no auto)
TARGET_LANGS = ["en", "zh", "ja", "ko", "ru", "cht"]

# ── Character ranges for detection ──
_CJK = [(0x4E00, 0x9FFF), (0x3400, 0x4DBF), (0xF900, 0xFAFF)]
_HANGUL = (0xAC00, 0xD7AF)
_CYRILLIC = (0x0400, 0x04FF)
_HIRA = (0x3040, 0x309F)
_KATA = (0x30A0, 0x30FF)
_TRAD = set("東國學區機華發車時書會經濟開間關點電無問題與從長見報場設定門經動進實")


def detect_language(text: str) -> str:
    """Auto-detect language code from text."""
    if not text.strip():
        return "zh"
    cjk = hira = kata = hangul = cyrillic = latin = 0
    for ch in text:
        cp = ord(ch)
        if any(s <= cp <= e for s, e in _CJK):
            cjk += 1
        elif _HIRA[0] <= cp <= _HIRA[1]:
            hira += 1
        elif _KATA[0] <= cp <= _KATA[1]:
            kata += 1
        elif _HANGUL[0] <= cp <= _HANGUL[1]:
            hangul += 1
        elif _CYRILLIC[0] <= cp <= _CYRILLIC[1]:
            cyrillic += 1
        elif ch.isascii() and ch.isalpha():
            latin += 1
    if hira or kata:
        return "ja"
    if hangul:
        return "ko"
    if cyrillic > len(text.replace(" ", "")) * 0.3:
        return "ru"
    if cjk:
        trad = sum(1 for ch in text if ch in _TRAD)
        return "cht" if trad > cjk * 0.3 else "zh"
    return "en" if latin else "zh"


def get_api_code(lang: str, api: str) -> str:
    """Get API-specific language code."""
    return LANGUAGES.get(lang, {}).get(api, lang)


def get_lang_name(lang: str) -> str:
    """Get display name for a language code."""
    return LANGUAGES.get(lang, {}).get("name", lang)


def get_default_target(source: str) -> str:
    """Get default target language based on source."""
    return "en" if source == "zh" else "zh"
