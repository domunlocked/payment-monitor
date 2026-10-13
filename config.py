"""Load and validate local-only listener configuration."""

from dataclasses import dataclass
import os
from pathlib import Path
import re

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    api_id: int | None
    api_hash: str | None
    chat_id: int | str | None
    api_token: str
    api_host: str
    api_port: int
    database_path: Path
    retention_days: int
    log_level: str
    session_path: Path
    logs_path: Path


def get_settings(
    *, require_telegram: bool = False, require_chat: bool = True
) -> Settings:
    """Read local settings and optionally require Telegram listener configuration."""
    raw_id = os.getenv("TELEGRAM_API_ID", "").strip()
    api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
    raw_chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    token = os.getenv("API_TOKEN", "").strip()
    api_id: int | None = None
    if raw_id:
        try:
            api_id = int(raw_id)
        except ValueError as exc:
            raise ValueError("TELEGRAM_API_ID must be a number.") from exc
        if api_id <= 0:
            raise ValueError("TELEGRAM_API_ID must be a positive number.")
    if api_hash and len(api_hash) < 20:
        raise ValueError("TELEGRAM_API_HASH does not look valid; check your .env file.")
    if require_telegram:
        missing = []
        if api_id is None:
            missing.append("TELEGRAM_API_ID")
        if not api_hash:
            missing.append("TELEGRAM_API_HASH")
        if require_chat and not raw_chat_id:
            missing.append("TELEGRAM_CHAT_ID")
        if missing:
            raise ValueError(f"Set {', '.join(missing)} in .env before starting Telegram.")
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
    if api_port != 8765:
        raise ValueError("API_PORT must be 8765 for the local dashboard.")
    if retention_days < 1:
        raise ValueError("RETENTION_DAYS must be at least 1.")
    api_host = os.getenv("API_HOST", "127.0.0.1").strip()
    if api_host != "127.0.0.1":
        raise ValueError("API_HOST must be 127.0.0.1; public and LAN binds are disabled.")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL.")

    database_path = Path(os.getenv("DATABASE_PATH", "payment_history.sqlite3"))
    if not database_path.is_absolute():
        database_path = PROJECT_DIR / database_path
    chat_id: int | str | None = raw_chat_id or None
    if raw_chat_id:
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
        api_host=api_host,
        api_port=api_port,
        database_path=database_path,
        retention_days=retention_days,
        log_level=log_level,
        session_path=PROJECT_DIR / "payment-monitor.session",
        logs_path=PROJECT_DIR / "logs",
    )
