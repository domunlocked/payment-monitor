import asyncio
from types import SimpleNamespace

import pytest

from config import Settings
from database import PaymentDatabase
from listener import TelegramListenerManager


class FakeTelegramClient:
    def __init__(self, *, authorized: bool = True) -> None:
        self.authorized = authorized
        self.connected = False
        self.handler = None
        self.disconnect_event = asyncio.Event()

    async def connect(self) -> None:
        self.connected = True

    async def get_messages(self, _chat, *, limit: int) -> list[object]:
        assert limit == 1
        return [SimpleNamespace(id=10)]

    async def is_user_authorized(self) -> bool:
        return self.authorized

    def add_event_handler(self, handler, _event) -> None:
        self.handler = handler

    async def run_until_disconnected(self) -> None:
        await self.disconnect_event.wait()

    def is_connected(self) -> bool:
        return self.connected

    async def disconnect(self) -> None:
        self.connected = False


def settings(tmp_path, *, configured: bool = True) -> Settings:
    return Settings(
        api_id=12345 if configured else None,
        api_hash="test-only-telegram-hash-value" if configured else None,
        chat_id=-1001234567890 if configured else None,
        api_token="test-only-token-with-more-than-thirty-two-characters",
        api_host="127.0.0.1",
        api_port=8765,
        database_path=tmp_path / "history.sqlite3",
        retention_days=365,
        log_level="INFO",
        session_path=tmp_path / "payment-monitor.session",
        logs_path=tmp_path / "logs",
    )


async def wait_for_state(manager: TelegramListenerManager, expected: str) -> None:
    for _ in range(100):
        if manager.status()["listener_state"] == expected:
            return
        await asyncio.sleep(0.005)
    raise AssertionError(f"Listener did not reach {expected!r}: {manager.status()!r}")


def test_start_is_idempotent_processes_new_messages_and_stop_keeps_latest(tmp_path) -> None:
    clients = []

    def make_client(*_args, **_kwargs):
        client = FakeTelegramClient()
        clients.append(client)
        return client

    async def run() -> tuple[dict, dict]:
        database = PaymentDatabase(tmp_path / "history.sqlite3")
        manager = TelegramListenerManager(
            settings(tmp_path), database, client_factory=make_client
        )
        await manager.start()
        await manager.start()
        await wait_for_state(manager, "connected")
        assert len(clients) == 1
        assert clients[0].handler is not None
        await clients[0].handler(
            SimpleNamespace(
                id=10,
                raw_text=(
                    "$12.50 paid by Example Customer (*844) on Oct 04, 01:55 PM "
                    "via ABA KHQR (Example Bank Plc) at Example Shop. "
                    "Trx. ID: 100000000000001, APV: 512666."
                )
            )
        )
        await clients[0].handler(
            SimpleNamespace(
                id=12,
                raw_text=(
                    "$12.50 paid by Example Customer (*844) on Oct 04, 01:55 PM "
                    "via ABA KHQR (Example Bank Plc) at Example Shop. "
                    "Trx. ID: 100000000000001, APV: 512666."
                )
            )
        )
        stopped = await manager.stop()
        await manager.start()
        await wait_for_state(manager, "connected")
        assert len(clients) == 2
        stopped = await manager.stop()
        _, rows = database.latest(limit=1)
        return stopped, {"count": len(rows), "id": rows[0]["transaction_id"]}

    stopped, saved = asyncio.run(run())
    assert stopped["listener_state"] == "stopped"
    assert stopped["telegram_connected"] is False
    assert saved == {"count": 1, "id": "100000000000001"}


def test_process_lock_prevents_a_second_service_instance(tmp_path) -> None:
    from listener import SingleInstanceLock

    path = tmp_path / "logs" / "service.lock"
    first = SingleInstanceLock(path)
    second = SingleInstanceLock(path)
    assert first.acquire() is True
    try:
        assert second.acquire() is False
    finally:
        first.release()
    assert second.acquire() is True
    second.release()


def test_missing_telegram_settings_are_reported_without_starting_client(tmp_path) -> None:
    made_client = False

    def make_client(*_args, **_kwargs):
        nonlocal made_client
        made_client = True
        raise AssertionError("Telegram client must not start with missing settings.")

    async def run() -> None:
        manager = TelegramListenerManager(
            settings(tmp_path, configured=False),
            PaymentDatabase(tmp_path / "history.sqlite3"),
            client_factory=make_client,
        )
        with pytest.raises(ValueError, match="TELEGRAM_API_ID.*TELEGRAM_API_HASH.*TELEGRAM_CHAT_ID"):
            await manager.start()
        assert manager.status()["listener_state"] == "setup_required"
        assert manager.status()["listener_running"] is False

    asyncio.run(run())
    assert made_client is False


def test_unauthorized_session_requires_explicit_local_login(tmp_path) -> None:
    clients = []

    def make_client(*_args, **_kwargs):
        client = FakeTelegramClient(authorized=False)
        clients.append(client)
        return client

    async def run() -> dict:
        manager = TelegramListenerManager(
            settings(tmp_path),
            PaymentDatabase(tmp_path / "history.sqlite3"),
            client_factory=make_client,
        )
        await manager.start()
        await wait_for_state(manager, "needs_login")
        return manager.status()

    status = asyncio.run(run())
    assert len(clients) == 1
    assert status["listener_running"] is False
    assert "listener.py --login" in status["message"]


def test_new_event_keeps_source_message_ids_for_duplicate_protection(tmp_path) -> None:
    async def run() -> tuple[dict, list[dict]]:
        database = PaymentDatabase(tmp_path / "history.sqlite3")
        manager = TelegramListenerManager(
            settings(tmp_path),
            database,
        )
        event = SimpleNamespace(
            id=77,
            chat_id=-1001234567890,
            raw_text=(
                "$12.50 paid by Private Customer (*844) on Oct 04, 01:55 PM "
                "via ABA KHQR (Private Bank Plc) at Private Merchant. "
                "Trx. ID: 100000000000077, APV: 512666."
            ),
        )
        await manager._handle_message(event)
        duplicate = SimpleNamespace(
            id=77,
            chat_id=-1001234567890,
            raw_text=event.raw_text,
        )
        await manager._handle_message(duplicate)
        _, payments = database.latest(limit=1)
        return payments[0], payments

    payment, payments = asyncio.run(run())
    assert payment["source_chat_id"] == "-1001234567890"
    assert payment["source_message_id"] == "77"
    assert len(payments) == 1
    assert payment["transaction_id"] == "100000000000077"
