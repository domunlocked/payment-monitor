from pathlib import Path

from fastapi.testclient import TestClient

from api import create_app
from database import PaymentDatabase

API_TOKEN = "test-only-token-with-more-than-thirty-two-characters"
API_ORIGIN = "http://127.0.0.1:8765"
PAYMENT = {
    "currency": "KHR",
    "amount": "50000",
    "payment_status": "Paid",
    "customer_name": "Example Customer",
    "account_suffix": None,
    "payment_method": "ABA PAY",
    "bank_name": None,
    "merchant_name": "Example Shop",
    "payment_datetime": "Oct 04, 01:36 PM",
    "transaction_id": "100000000000101",
    "approval_code": "211408",
}


class FakeListener:
    def __init__(self, connected: bool = False) -> None:
        self.running = connected
        self.connected = connected
        self.start_calls = 0
        self.stop_calls = 0
        self.message = "Connected to the configured Telegram group." if connected else "Listener is stopped."

    def status(self) -> dict[str, object]:
        return {
            "listener_state": "connected" if self.connected else "stopped",
            "listener_running": self.running,
            "telegram_connected": self.connected,
            "message": self.message,
        }

    async def start(self) -> dict[str, object]:
        self.start_calls += 1
        self.running = True
        self.connected = True
        self.message = "Connected to the configured Telegram group."
        return self.status()

    async def stop(self) -> dict[str, object]:
        self.stop_calls += 1
        self.running = False
        self.connected = False
        self.message = "Listener is stopped."
        return self.status()


def make_client(tmp_path, listener: FakeListener | None = None) -> TestClient:
    database = PaymentDatabase(tmp_path / "history.sqlite3")
    database.add_payment(PAYMENT)
    app = create_app(
        database,
        API_TOKEN,
        listener=listener or FakeListener(connected=True),
        static_dir=Path(__file__).resolve().parents[1],
        api_origin=API_ORIGIN,
    )
    return TestClient(app, base_url=API_ORIGIN)


def dashboard_headers() -> dict[str, str]:
    return {"Origin": API_ORIGIN, "Sec-Fetch-Site": "same-origin"}


def test_private_routes_require_local_dashboard_session(tmp_path) -> None:
    client = make_client(tmp_path)
    assert client.get("/api/status").status_code == 401
    assert client.get("/api/latest-payment").status_code == 401

    page = client.get("/")
    assert page.status_code == 200
    cookie = page.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=strict" in cookie
    assert client.get("/api/status").status_code == 200
    assert client.get("/healthz").json() == {
        "status": "ok",
        "service": "payment-monitor",
    }


def test_status_latest_and_existing_history_endpoints(tmp_path) -> None:
    client = make_client(tmp_path)
    client.get("/")

    status = client.get("/api/status")
    assert status.json()["telegram_connected"] is True
    assert status.json()["listener_running"] is True

    latest = client.get("/api/latest-payment")
    assert latest.status_code == 200
    assert latest.json()["payment"]["transaction_id"] == PAYMENT["transaction_id"]
    assert latest.json()["payment"]["payment_status"] == "Paid"
    assert latest.json()["payment"]["announcement"] == "ទទួលបានប្រាក់ ប្រាំម៉ឺនរៀល"

    history = client.get("/api/payments")
    assert history.json()["payments"][0]["transaction_id"] == PAYMENT["transaction_id"]
    assert client.get("/api/payments.csv").status_code == 200


def test_latest_payment_endpoint_returns_empty_state(tmp_path) -> None:
    database = PaymentDatabase(tmp_path / "empty.sqlite3")
    app = create_app(
        database,
        API_TOKEN,
        listener=FakeListener(),
        static_dir=Path(__file__).resolve().parents[1],
        api_origin=API_ORIGIN,
    )
    client = TestClient(app, base_url=API_ORIGIN)
    client.get("/")
    assert client.get("/api/latest-payment").json() == {"payment": None}


def test_start_and_stop_are_same_origin_and_keep_latest_payment(tmp_path) -> None:
    listener = FakeListener()
    client = make_client(tmp_path, listener)
    client.get("/")

    denied = client.post(
        "/api/listener/start",
        headers={"Origin": "https://untrusted.example", "Sec-Fetch-Site": "cross-site"},
    )
    assert denied.status_code == 403
    assert listener.start_calls == 0

    started = client.post("/api/listener/start", headers=dashboard_headers())
    assert started.status_code == 200
    assert started.json()["telegram_connected"] is True
    stopped = client.post("/api/listener/stop", headers=dashboard_headers())
    assert stopped.status_code == 200
    assert stopped.json()["listener_running"] is False
    assert listener.start_calls == 1
    assert listener.stop_calls == 1
    assert client.get("/api/latest-payment").json()["payment"]["transaction_id"] == PAYMENT[
        "transaction_id"
    ]


def test_autostart_starts_listener_and_shutdown_stops_it(tmp_path) -> None:
    listener = FakeListener()
    database = PaymentDatabase(tmp_path / "auto-start.sqlite3")
    app = create_app(
        database,
        API_TOKEN,
        listener=listener,
        static_dir=Path(__file__).resolve().parents[1],
        api_origin=API_ORIGIN,
        auto_start_listener=True,
    )
    with TestClient(app, base_url=API_ORIGIN) as client:
        client.get("/")
        assert client.get("/api/status").json()["telegram_connected"] is True
        assert listener.start_calls == 1
    assert listener.stop_calls == 1


def test_start_endpoint_reports_missing_telegram_settings(tmp_path) -> None:
    class UnconfiguredListener(FakeListener):
        async def start(self) -> dict[str, object]:
            raise ValueError("Set TELEGRAM_CHAT_ID in .env before starting Telegram.")

    client = make_client(tmp_path, UnconfiguredListener())
    client.get("/")
    response = client.post("/api/listener/start", headers=dashboard_headers())
    assert response.status_code == 409
    assert response.json()["detail"] == "Set TELEGRAM_CHAT_ID in .env before starting Telegram."


def test_local_host_and_no_cors_are_enforced(tmp_path) -> None:
    client = make_client(tmp_path)
    client.get("/")
    bad_host = client.get("http://localhost:8765/api/status")
    assert bad_host.status_code == 421

    preflight = client.options(
        "/api/status",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in preflight.headers


def test_local_dashboard_serves_only_static_files(tmp_path) -> None:
    client = make_client(tmp_path)
    assert client.get("/").status_code == 200
    assert client.get("/styles.css").status_code == 200
    assert client.get("/app.js").status_code == 200
    assert client.get("/.env").status_code == 404
    assert client.get("/payment_history.sqlite3").status_code == 404
    assert client.get("/styles.css?path=../../.env").status_code == 200
