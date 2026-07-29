"""
Picks the active TTS engine based on the TTS_ENGINE env var. This is
the ONLY place that decides which concrete engine gets used — handlers
call get_tts_engine() and work against the TTSEngine interface only.
"""

from functools import lru_cache

from app.config import settings
from app.tts.base import TTSEngine
from app.tts.gtts_engine import GTTSEngine
from app.tts.openai_engine import OpenAITTSEngine


@lru_cache
def get_tts_engine() -> TTSEngine:
    if settings.TTS_ENGINE.lower() == "openai":
        return OpenAITTSEngine(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_TTS_MODEL)
    return GTTSEngine()
