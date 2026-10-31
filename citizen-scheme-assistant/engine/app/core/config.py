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
    os.environ.setdefault("SCHEME_DEMO_ENABLED", "1")


def cors_origins() -> list[str]:
    origins = [o.strip() for o in os.getenv("CORS_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()]
    for origin in origins:
        parsed = urlsplit(origin)
        if (parsed.scheme not in ("http", "https") or not parsed.hostname
                or parsed.username or parsed.password or parsed.path
                or parsed.query or parsed.fragment or "*" in origin):
            raise ValueError("CORS_ORIGINS must contain explicit HTTP(S) origins")
    return origins
