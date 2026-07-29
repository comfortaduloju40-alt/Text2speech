"""
OpenAI TTS engine. Higher-quality, multilingual voices. Requires
OPENAI_API_KEY. Uses raw HTTP via `requests` rather than the openai
SDK, to keep the dependency list small.
"""

import requests

from app.tts.base import TTSEngine, Voice

_OPENAI_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


class OpenAITTSEngine(TTSEngine):
    name = "openai"
    native_format = "mp3"

    def __init__(self, api_key: str | None, model: str = "tts-1"):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when TTS_ENGINE=openai")
        self.api_key = api_key
        self.model = model

    def list_voices(self) -> list[Voice]:
        return [Voice(id=v, label=v.capitalize(), language_code="*") for v in _OPENAI_VOICES]

    def list_languages(self) -> list[tuple[str, str]]:
        # OpenAI TTS auto-detects language from the input text — there's
        # no separate language parameter to set.
        return [("auto", "Auto-detected (multilingual)")]

    def synthesize(self, text: str, voice_id: str, language_code: str) -> bytes:
        response = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "voice": voice_id,
                "input": text,
                "response_format": "mp3",
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.content
