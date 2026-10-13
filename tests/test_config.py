import pytest

from config import get_settings


def test_local_api_can_start_before_telegram_is_configured(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("TELEGRAM_API_ID", raising=False)
    monkeypatch.delenv("TELEGRAM_API_HASH", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.setenv("API_TOKEN", "test-only-token-with-more-than-thirty-two-characters")
    monkeypatch.setenv("API_HOST", "127.0.0.1")
    monkeypatch.setenv("API_PORT", "8765")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "history.sqlite3"))

    settings = get_settings()
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8765
    assert settings.api_id is None
    assert settings.chat_id is None

    with pytest.raises(ValueError, match="TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_CHAT_ID"):
        get_settings(require_telegram=True)


def test_non_loopback_api_host_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("API_TOKEN", "test-only-token-with-more-than-thirty-two-characters")
    monkeypatch.setenv("API_HOST", "0.0.0.0")
    with pytest.raises(ValueError, match="API_HOST must be 127.0.0.1"):
        get_settings()


def test_dashboard_port_is_fixed_to_8765(monkeypatch) -> None:
    monkeypatch.setenv("API_TOKEN", "test-only-token-with-more-than-thirty-two-characters")
    monkeypatch.setenv("API_HOST", "127.0.0.1")
    monkeypatch.setenv("API_PORT", "8766")
    with pytest.raises(ValueError, match="API_PORT must be 8765"):
        get_settings()
