"""
Abstract TTS engine interface. Every engine (gTTS, OpenAI, future
additions) implements this — handlers never talk to gTTS/OpenAI
directly, only through this interface via app/tts/factory.py. This is
what makes swapping the TTS engine a one-line env var change.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Voice:
    id: str
    label: str
    language_code: str  # "*" means this voice works with any language


class TTSEngine(ABC):
    name: str
    native_format: str  # audio format this engine returns, e.g. "mp3"

    @abstractmethod
    def list_voices(self) -> list[Voice]:
        """Returns the voices this engine supports."""

    @abstractmethod
    def list_languages(self) -> list[tuple[str, str]]:
        """Returns (language_code, display_name) pairs this engine supports."""

    @abstractmethod
    def synthesize(self, text: str, voice_id: str, language_code: str) -> bytes:
        """Synthesizes `text` and returns raw audio bytes in `native_format`."""
