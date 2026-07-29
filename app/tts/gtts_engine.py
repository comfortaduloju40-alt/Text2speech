"""
gTTS (Google Translate TTS) engine. Free, no API key required.

gTTS doesn't have distinct named voices the way OpenAI's TTS does —
what we expose as "voices" here are language/accent (tld) combinations,
which is the closest gTTS gets to voice selection.
"""

import io

from gtts import gTTS
from gtts.lang import tts_langs

from app.tts.base import TTSEngine, Voice

# Maps our voice IDs to gTTS's `tld` parameter, which controls accent
# for languages with regional variants (mainly English).
_ACCENT_TLDS = {
    "us": "com",
    "uk": "co.uk",
    "au": "com.au",
    "in": "co.in",
    "ca": "ca",
    "default": "com",
}

_VOICES = [
    Voice(id="us", label="English (US)", language_code="en"),
    Voice(id="uk", label="English (UK)", language_code="en"),
    Voice(id="au", label="English (Australia)", language_code="en"),
    Voice(id="in", label="English (India)", language_code="en"),
    Voice(id="default", label="Standard (matches selected language)", language_code="*"),
]


class GTTSEngine(TTSEngine):
    name = "gtts"
    native_format = "mp3"

    def list_voices(self) -> list[Voice]:
        return _VOICES

    def list_languages(self) -> list[tuple[str, str]]:
        return sorted(tts_langs().items(), key=lambda pair: pair[1])

    def synthesize(self, text: str, voice_id: str, language_code: str) -> bytes:
        tld = _ACCENT_TLDS.get(voice_id, "com")
        tts = gTTS(text=text, lang=language_code, tld=tld)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        return buffer.getvalue()
