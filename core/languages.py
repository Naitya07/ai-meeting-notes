"""
MeetingMind - Language Support
Defines all languages supported for Whisper transcription and provides
lookup, display, and grouping utilities.
"""

from typing import Optional

# ---------------------------------------------------------------------------
# Master language registry
# ---------------------------------------------------------------------------
# Each key is the canonical two-letter (or zh-hans / zh-hant) code used
# throughout MeetingMind.  whisper_code is what gets passed to Whisper.
# ---------------------------------------------------------------------------

LANGUAGES: dict[str, dict] = {
    # ---- European (Western) ------------------------------------------------
    "en": {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "rtl": False,
        "whisper_code": "en",
        "region": "Europe & Americas",
        "popular": True,
    },
    "es": {
        "code": "es",
        "name": "Spanish",
        "native_name": "Español",
        "rtl": False,
        "whisper_code": "es",
        "region": "Europe & Americas",
        "popular": True,
    },
    "fr": {
        "code": "fr",
        "name": "French",
        "native_name": "Français",
        "rtl": False,
        "whisper_code": "fr",
        "region": "Europe & Americas",
        "popular": True,
    },
    "pt": {
        "code": "pt",
        "name": "Portuguese",
        "native_name": "Português",
        "rtl": False,
        "whisper_code": "pt",
        "region": "Europe & Americas",
        "popular": True,
    },
    "de": {
        "code": "de",
        "name": "German",
        "native_name": "Deutsch",
        "rtl": False,
        "whisper_code": "de",
        "region": "Europe & Americas",
        "popular": True,
    },
    "it": {
        "code": "it",
        "name": "Italian",
        "native_name": "Italiano",
        "rtl": False,
        "whisper_code": "it",
        "region": "Europe & Americas",
        "popular": False,
    },
    "nl": {
        "code": "nl",
        "name": "Dutch",
        "native_name": "Nederlands",
        "rtl": False,
        "whisper_code": "nl",
        "region": "Europe & Americas",
        "popular": False,
    },
    "sv": {
        "code": "sv",
        "name": "Swedish",
        "native_name": "Svenska",
        "rtl": False,
        "whisper_code": "sv",
        "region": "Europe & Americas",
        "popular": False,
    },
    "da": {
        "code": "da",
        "name": "Danish",
        "native_name": "Dansk",
        "rtl": False,
        "whisper_code": "da",
        "region": "Europe & Americas",
        "popular": False,
    },
    "no": {
        "code": "no",
        "name": "Norwegian",
        "native_name": "Norsk",
        "rtl": False,
        "whisper_code": "no",
        "region": "Europe & Americas",
        "popular": False,
    },
    "fi": {
        "code": "fi",
        "name": "Finnish",
        "native_name": "Suomi",
        "rtl": False,
        "whisper_code": "fi",
        "region": "Europe & Americas",
        "popular": False,
    },
    # ---- European (Eastern) -----------------------------------------------
    "ru": {
        "code": "ru",
        "name": "Russian",
        "native_name": "Русский",
        "rtl": False,
        "whisper_code": "ru",
        "region": "Eastern Europe",
        "popular": True,
    },
    "pl": {
        "code": "pl",
        "name": "Polish",
        "native_name": "Polski",
        "rtl": False,
        "whisper_code": "pl",
        "region": "Eastern Europe",
        "popular": False,
    },
    "uk": {
        "code": "uk",
        "name": "Ukrainian",
        "native_name": "Українська",
        "rtl": False,
        "whisper_code": "uk",
        "region": "Eastern Europe",
        "popular": False,
    },
    "cs": {
        "code": "cs",
        "name": "Czech",
        "native_name": "Čeština",
        "rtl": False,
        "whisper_code": "cs",
        "region": "Eastern Europe",
        "popular": False,
    },
    "ro": {
        "code": "ro",
        "name": "Romanian",
        "native_name": "Română",
        "rtl": False,
        "whisper_code": "ro",
        "region": "Eastern Europe",
        "popular": False,
    },
    "hu": {
        "code": "hu",
        "name": "Hungarian",
        "native_name": "Magyar",
        "rtl": False,
        "whisper_code": "hu",
        "region": "Eastern Europe",
        "popular": False,
    },
    "el": {
        "code": "el",
        "name": "Greek",
        "native_name": "Ελληνικά",
        "rtl": False,
        "whisper_code": "el",
        "region": "Eastern Europe",
        "popular": False,
    },
    # ---- Middle East & Central Asia ---------------------------------------
    "ar": {
        "code": "ar",
        "name": "Arabic",
        "native_name": "العربية",
        "rtl": True,
        "whisper_code": "ar",
        "region": "Middle East & Africa",
        "popular": True,
    },
    "he": {
        "code": "he",
        "name": "Hebrew",
        "native_name": "עברית",
        "rtl": True,
        "whisper_code": "he",
        "region": "Middle East & Africa",
        "popular": False,
    },
    "fa": {
        "code": "fa",
        "name": "Persian",
        "native_name": "فارسی",
        "rtl": True,
        "whisper_code": "fa",
        "region": "Middle East & Africa",
        "popular": False,
    },
    "ur": {
        "code": "ur",
        "name": "Urdu",
        "native_name": "اردو",
        "rtl": True,
        "whisper_code": "ur",
        "region": "South Asia",
        "popular": False,
    },
    "tr": {
        "code": "tr",
        "name": "Turkish",
        "native_name": "Türkçe",
        "rtl": False,
        "whisper_code": "tr",
        "region": "Middle East & Africa",
        "popular": False,
    },
    # ---- South Asia -------------------------------------------------------
    "hi": {
        "code": "hi",
        "name": "Hindi",
        "native_name": "हिन्दी",
        "rtl": False,
        "whisper_code": "hi",
        "region": "South Asia",
        "popular": True,
    },
    "bn": {
        "code": "bn",
        "name": "Bengali",
        "native_name": "বাংলা",
        "rtl": False,
        "whisper_code": "bn",
        "region": "South Asia",
        "popular": False,
    },
    "ta": {
        "code": "ta",
        "name": "Tamil",
        "native_name": "தமிழ்",
        "rtl": False,
        "whisper_code": "ta",
        "region": "South Asia",
        "popular": False,
    },
    "te": {
        "code": "te",
        "name": "Telugu",
        "native_name": "తెలుగు",
        "rtl": False,
        "whisper_code": "te",
        "region": "South Asia",
        "popular": False,
    },
    # ---- East Asia --------------------------------------------------------
    "zh-hans": {
        "code": "zh-hans",
        "name": "Chinese (Simplified)",
        "native_name": "简体中文",
        "rtl": False,
        "whisper_code": "zh",
        "region": "East Asia",
        "popular": True,
    },
    "zh-hant": {
        "code": "zh-hant",
        "name": "Chinese (Traditional)",
        "native_name": "繁體中文",
        "rtl": False,
        "whisper_code": "zh",
        "region": "East Asia",
        "popular": False,
    },
    "ja": {
        "code": "ja",
        "name": "Japanese",
        "native_name": "日本語",
        "rtl": False,
        "whisper_code": "ja",
        "region": "East Asia",
        "popular": True,
    },
    "ko": {
        "code": "ko",
        "name": "Korean",
        "native_name": "한국어",
        "rtl": False,
        "whisper_code": "ko",
        "region": "East Asia",
        "popular": False,
    },
    # ---- South-East Asia --------------------------------------------------
    "vi": {
        "code": "vi",
        "name": "Vietnamese",
        "native_name": "Tiếng Việt",
        "rtl": False,
        "whisper_code": "vi",
        "region": "South-East Asia",
        "popular": False,
    },
    "th": {
        "code": "th",
        "name": "Thai",
        "native_name": "ภาษาไทย",
        "rtl": False,
        "whisper_code": "th",
        "region": "South-East Asia",
        "popular": False,
    },
    "id": {
        "code": "id",
        "name": "Indonesian",
        "native_name": "Bahasa Indonesia",
        "rtl": False,
        "whisper_code": "id",
        "region": "South-East Asia",
        "popular": False,
    },
    "ms": {
        "code": "ms",
        "name": "Malay",
        "native_name": "Bahasa Melayu",
        "rtl": False,
        "whisper_code": "ms",
        "region": "South-East Asia",
        "popular": False,
    },
    "tl": {
        "code": "tl",
        "name": "Tagalog",
        "native_name": "Tagalog",
        "rtl": False,
        "whisper_code": "tl",
        "region": "South-East Asia",
        "popular": False,
    },
    # ---- Africa -----------------------------------------------------------
    "sw": {
        "code": "sw",
        "name": "Swahili",
        "native_name": "Kiswahili",
        "rtl": False,
        "whisper_code": "sw",
        "region": "Middle East & Africa",
        "popular": False,
    },
}

# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

# Whisper accepts plain "zh" for both Simplified and Traditional.
# Build a secondary lookup from whisper_code → first matching MeetingMind code
# so round-trips work cleanly when Whisper returns its detected language.
_WHISPER_TO_CODE: dict[str, str] = {}
for _code, _lang in LANGUAGES.items():
    _wc = _lang["whisper_code"]
    if _wc not in _WHISPER_TO_CODE:
        _WHISPER_TO_CODE[_wc] = _code


def get_language(code: str) -> Optional[dict]:
    """
    Return the language info dict for the given MeetingMind language code.

    Falls back to a whisper_code lookup so that codes returned by Whisper
    (e.g. "zh") are also resolved gracefully.

    Args:
        code: Language code such as "en", "zh-hans", or a Whisper code "zh".

    Returns:
        Language info dict, or None if the code is unknown.
    """
    if code in LANGUAGES:
        return LANGUAGES[code]
    # Try whisper_code fallback
    fallback_code = _WHISPER_TO_CODE.get(code)
    if fallback_code:
        return LANGUAGES[fallback_code]
    return None


def get_all_languages() -> list[dict]:
    """
    Return all languages sorted alphabetically by English name.

    Returns:
        List of language info dicts.
    """
    return sorted(LANGUAGES.values(), key=lambda lang: lang["name"])


def get_language_display(code: str) -> str:
    """
    Return a display string in the format "Native Name (English Name)".

    Args:
        code: MeetingMind language code.

    Returns:
        Formatted string, e.g. "Français (French)".
        Falls back to the raw code if the language is not found.
    """
    lang = get_language(code)
    if not lang:
        return code
    native = lang["native_name"]
    english = lang["name"]
    if native == english:
        return english
    return f"{native} ({english})"


def get_popular_languages(top_n: int = 10) -> list[dict]:
    """
    Return the most commonly used languages, ordered by name.

    The set of "popular" languages is defined by the ``popular`` flag in
    the LANGUAGES registry.  If fewer than top_n languages are marked
    popular, the remainder are filled from the alphabetically sorted full
    list so the return length always equals min(top_n, total).

    Args:
        top_n: Maximum number of languages to return.

    Returns:
        List of language info dicts.
    """
    popular = [lang for lang in LANGUAGES.values() if lang.get("popular")]
    popular.sort(key=lambda l: l["name"])

    if len(popular) >= top_n:
        return popular[:top_n]

    # Pad with remaining languages not already in the popular list
    popular_codes = {l["code"] for l in popular}
    extras = sorted(
        (l for l in LANGUAGES.values() if l["code"] not in popular_codes),
        key=lambda l: l["name"],
    )
    return (popular + extras)[:top_n]


def is_rtl(code: str) -> bool:
    """
    Return True if the language is written right-to-left.

    Args:
        code: MeetingMind language code.

    Returns:
        True for RTL languages (Arabic, Hebrew, Persian, Urdu), False otherwise.
        Defaults to False for unknown codes.
    """
    lang = get_language(code)
    return bool(lang and lang.get("rtl"))


def get_whisper_code(code: str) -> str:
    """
    Return the Whisper-compatible language code for the given MeetingMind code.

    Args:
        code: MeetingMind language code such as "zh-hans".

    Returns:
        Whisper language code string (e.g. "zh"), or the input code unchanged
        if the language is not found.
    """
    lang = get_language(code)
    if lang:
        return lang["whisper_code"]
    return code


def group_by_region() -> dict[str, list[dict]]:
    """
    Return all languages grouped by geographic region.

    Returns:
        Dict mapping region name to a list of language info dicts sorted
        alphabetically by English name within each region.

    Example::

        {
            "East Asia": [
                {"code": "ja", "name": "Japanese", ...},
                {"code": "ko", "name": "Korean", ...},
                ...
            ],
            ...
        }
    """
    groups: dict[str, list[dict]] = {}
    for lang in LANGUAGES.values():
        region = lang.get("region", "Other")
        groups.setdefault(region, []).append(lang)

    # Sort languages within each region
    for region in groups:
        groups[region].sort(key=lambda l: l["name"])

    # Return regions in alphabetical order
    return dict(sorted(groups.items()))
