"""ElevenLabs Text-to-Speech (TTS) Service for Shayak Voice Assistant.

Provides clear, sweet female multilingual voice generation for English, Hindi,
and Hinglish. Includes text sanitization, response trimming for natural speech,
in-memory audio caching, and graceful fallback when offline.
"""
import hashlib
import json
import re
import urllib.error
import urllib.request
from typing import Any

from app.core.config import (
    elevenlabs_api_key,
    elevenlabs_model_id,
    elevenlabs_voice_id,
)


class ElevenLabsService:
    """Orchestrates ElevenLabs TTS generation for Shayak AI Voice Assistant."""

    def __init__(self) -> None:
        # In-memory LRU-like audio cache to prevent redundant API calls
        self._cache: dict[str, bytes] = {}
        self._max_cache_entries = 100

    def is_configured(self) -> bool:
        """Check if ElevenLabs API key is present in environment."""
        return bool(elevenlabs_api_key())

    def get_status(self) -> dict[str, Any]:
        """Return public metadata about the configured voice."""
        return {
            "configured": self.is_configured(),
            "provider": "elevenlabs",
            "voice_id": elevenlabs_voice_id(),
            "model_id": elevenlabs_model_id(),
            "gender": "female",
            "persona": "Sahayak Voice Assistant (Sweet, Clear & Multilingual)",
            "languages_supported": ["en", "hi", "hinglish"],
        }

    def sanitize_for_speech(self, text: str, lang: str = "en") -> str:
        """Strip markdown syntax, raw URLs, table formatting, and emojis for natural speech."""
        if not text:
            return ""

        t = text.strip()

        # 1. Replace markdown links [label](url) with label
        t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)

        # 2. Remove raw URLs
        t = re.sub(r"https?://\S+", "", t)

        # 3. Replace currency symbols with spoken words
        if lang == "hi" or any("\u0900" <= c <= "\u097f" for c in t):
            t = re.sub(r"₹\s*([0-9,]+)", r"\1 रुपये", t)
            t = re.sub(r"Rs\.?\s*([0-9,]+)", r"\1 रुपये", t)
        else:
            t = re.sub(r"₹\s*([0-9,]+)", r"\1 rupees", t)
            t = re.sub(r"Rs\.?\s*([0-9,]+)", r"\1 rupees", t)

        # 4. Remove markdown headers, bold, italics, backticks, blockquotes
        t = re.sub(r"^#+\s*", "", t, flags=re.MULTILINE)
        t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
        t = re.sub(r"\*([^*]+)\*", r"\1", t)
        t = re.sub(r"`([^`]+)`", r"\1", t)
        t = re.sub(r"^>\s*", "", t, flags=re.MULTILINE)

        # 5. Remove bullet points and numbered list markers
        t = re.sub(r"^\s*[-*•]\s+", "", t, flags=re.MULTILINE)
        t = re.sub(r"^\s*\d+\.\s+", "", t, flags=re.MULTILINE)

        # 6. Remove emojis and special decorative glyphs
        emoji_pattern = re.compile(
            "["
            "\U00010000-\U0010FFFF"
            "\u2600-\u26FF"
            "\u2700-\u27BF"
            "\uFE00-\uFE0F"
            "\u200D"
            "\u2300-\u23FF"
            "]+",
            flags=re.UNICODE,
        )
        t = emoji_pattern.sub("", t)

        # 7. Collapse multiple spaces and newlines into clean sentences
        t = re.sub(r"\s*\n\s*", " ", t)
        t = re.sub(r"\s+", " ", t).strip()

        # 8. Conversational length optimization:
        # If text is very long (e.g. scheme tables or multi-step lists), speak the core answer
        # (up to ~320 chars ending on a complete sentence) so the voice is brisk and engaging.
        if len(t) > 350:
            sentences = re.split(r"(?<=[.!?।])\s+", t)
            clipped = ""
            for s in sentences:
                if len(clipped) + len(s) + 1 <= 320:
                    clipped = f"{clipped} {s}".strip()
                else:
                    break
            if clipped:
                t = clipped
            else:
                t = t[:320].rsplit(" ", 1)[0] + ("।" if lang == "hi" else ".")

        return t

    def synthesize_speech(
        self,
        text: str,
        lang: str = "en",
        voice_id: str | None = None,
    ) -> tuple[bytes | None, str]:
        """Synthesize text into MP3 audio via ElevenLabs API.

        Returns (audio_bytes, sanitized_text). If ElevenLabs API key is missing
        or request fails, returns (None, sanitized_text) allowing client fallback.
        """
        sanitized = self.sanitize_for_speech(text, lang)
        if not sanitized:
            return None, ""

        active_voice = (voice_id or elevenlabs_voice_id()).strip()
        active_model = elevenlabs_model_id()
        api_key = elevenlabs_api_key()

        # Cache key based on voice, model, and sanitized text
        cache_key = hashlib.md5(f"{active_voice}:{active_model}:{sanitized}".encode("utf-8")).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key], sanitized

        if not api_key:
            # Not configured; return None so caller can use client-side SpeechSynthesis
            return None, sanitized

        endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{active_voice}"
        payload = {
            "text": sanitized,
            "model_id": active_model,
            "voice_settings": {
                "stability": 0.55,
                "similarity_boost": 0.85,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        }

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "User-Agent": "YojanaMitra-ShayakVoice/1.0",
        }

        req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=9.0) as res:
                if res.status == 200:
                    audio_bytes = res.read()
                    if audio_bytes and len(audio_bytes) > 200:
                        # Manage cache size
                        if len(self._cache) >= self._max_cache_entries:
                            # Pop oldest entry
                            first_key = next(iter(self._cache))
                            self._cache.pop(first_key, None)
                        self._cache[cache_key] = audio_bytes
                        return audio_bytes, sanitized
        except urllib.error.HTTPError as e:
            print(f"[ElevenLabsService] HTTPError {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            print(f"[ElevenLabsService] URLError: {e.reason}")
        except Exception as e:
            print(f"[ElevenLabsService] Unexpected error: {e}")

        return None, sanitized


elevenlabs_service = ElevenLabsService()
