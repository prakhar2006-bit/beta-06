"""Load local configuration without logging secrets or requiring a database."""
import os
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

ENGINE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_ORIGINS = (
    "http://localhost:3001,http://127.0.0.1:3001,"
    "http://localhost:3000,http://127.0.0.1:3000,"
    "http://localhost:3001,http://127.0.0.1:3001,"
    "http://localhost:3002,http://127.0.0.1:3002,"
    "http://localhost:5173,http://127.0.0.1:5173,"
    "http://localhost:5174,http://127.0.0.1:5174"
)


def load_environment() -> None:
    load_dotenv(ENGINE_DIR / ".env", override=False, interpolate=False)
    os.environ.setdefault("SCHEME_APP_ENV", "development")
    # Draft/demo routes must be explicitly enabled for local previews. Keeping
    # the default off prevents them from intercepting published API tests and
    # ordinary production-style requests.
    os.environ.setdefault("SCHEME_DEMO_ENABLED", "0")


def cors_origins() -> list[str]:
    origins = [o.strip() for o in os.getenv("CORS_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()]
    for origin in origins:
        parsed = urlsplit(origin)
        if (parsed.scheme not in ("http", "https") or not parsed.hostname
                or parsed.username or parsed.password or parsed.path
                or parsed.query or parsed.fragment or "*" in origin):
            raise ValueError("CORS_ORIGINS must contain explicit HTTP(S) origins")
    return origins


def gemini_api_key() -> str | None:
    """Retrieve Gemini API key from environment without exposing secrets in logs."""
    key = os.getenv("GEMINI_API_KEY")
    return key.strip() if key and key.strip() else None


def gemini_model() -> str:
    """Configurable Gemini model name, defaulting to Google's fast multimodal model."""
    return os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip()


def elevenlabs_api_key() -> str | None:
    """Retrieve ElevenLabs API key from environment without exposing secrets in logs."""
    key = os.getenv("ELEVENLABS_API_KEY")
    return key.strip() if key and key.strip() else None


def elevenlabs_voice_id() -> str:
    """Configurable sweet female multilingual ElevenLabs voice ID. Default: Rachel (21m00Tcm4TlvDq8ikWAM)."""
    return os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM").strip()


def elevenlabs_model_id() -> str:
    """ElevenLabs model identifier supporting seamless English, Hindi, and Hinglish with the same voice."""
    return os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2").strip()
