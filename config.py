"""Load and validate local-only listener configuration."""

from dataclasses import dataclass
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    api_id: int
    api_hash: str
    chat_id: int | str
    api_token: str
    cors_origins: tuple[str, ...]
    api_host: str
    api_port: int
    database_path: Path
    retention_days: int
    log_level: str
    session_path: Path
    logs_path: Path


def get_settings() -> Settings:
    """Read required secrets and options without logging their values."""
    raw_id = os.getenv("TELEGRAM_API_ID", "").strip()
    api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
    raw_chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    token = os.getenv("API_TOKEN", "").strip()
    if not raw_id or not api_hash or not raw_chat_id:
        raise ValueError(
            "Set TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_CHAT_ID in .env."
        )
    try:
        api_id = int(raw_id)
    except ValueError as exc:
        raise ValueError("TELEGRAM_API_ID must be a number.") from exc
    if api_id <= 0:
        raise ValueError("TELEGRAM_API_ID must be a positive number.")
    if len(api_hash) < 20:
        raise ValueError("TELEGRAM_API_HASH does not look valid; check your .env file.")
    if len(token) < 32 or token == "replace-this-with-a-private-random-token":
        raise ValueError(
            "Set API_TOKEN to a private random value of at least 32 characters."
        )
    if not re.fullmatch(r"[A-Za-z0-9_-]+", token):
        raise ValueError("API_TOKEN may contain only letters, numbers, hyphens, and underscores.")
    try:
        api_port = int(os.getenv("API_PORT", "8765"))
        retention_days = int(os.getenv("RETENTION_DAYS", "365"))
    except ValueError as exc:
        raise ValueError("API_PORT and RETENTION_DAYS must be whole numbers.") from exc
    if not 1 <= api_port <= 65535:
        raise ValueError("API_PORT must be between 1 and 65535.")
    if retention_days < 1:
        raise ValueError("RETENTION_DAYS must be at least 1.")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL.")

    database_path = Path(os.getenv("DATABASE_PATH", "payment_history.sqlite3"))
    if not database_path.is_absolute():
        database_path = PROJECT_DIR / database_path
    cors_origins = tuple(
        origin.strip().rstrip("/")
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    )
    for origin in cors_origins:
        parsed_origin = urlsplit(origin)
        if (
            origin == "*"
            or parsed_origin.scheme not in {"http", "https"}
            or not parsed_origin.netloc
            or parsed_origin.username
            or parsed_origin.password
            or parsed_origin.path
            or parsed_origin.query
            or parsed_origin.fragment
        ):
            raise ValueError(
                "CORS_ORIGINS must contain exact HTTP(S) origins only; wildcards and paths are not allowed."
            )
    chat_id: int | str = raw_chat_id
    try:
        chat_id = int(raw_chat_id)
    except ValueError:
        if not raw_chat_id.startswith("@"):
            chat_id = f"@{raw_chat_id}"

    return Settings(
        api_id=api_id,
        api_hash=api_hash,
        chat_id=chat_id,
        api_token=token,
        cors_origins=cors_origins,
        api_host=os.getenv("API_HOST", "127.0.0.1").strip(),
        api_port=api_port,
        database_path=database_path,
        retention_days=retention_days,
        log_level=log_level,
        session_path=PROJECT_DIR / "payment-monitor.session",
        logs_path=PROJECT_DIR / "logs",
    )
