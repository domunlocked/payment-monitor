from pathlib import Path

from fastapi.testclient import TestClient

from api import create_app
from database import PaymentDatabase


API_TOKEN = "test-only-token-with-more-than-thirty-two-characters"
PAYMENT = {
    "currency": "KHR",
    "amount": "50000",
    "customer_name": "Example Customer",
    "account_suffix": None,
    "payment_method": "ABA PAY",
    "bank_name": None,
    "merchant_name": "Example Shop",
    "payment_datetime": "Oct 04, 01:36 PM",
    "transaction_id": "100000000000101",
    "approval_code": "211408",
}


def make_client(tmp_path) -> TestClient:
    database = PaymentDatabase(tmp_path / "history.sqlite3")
    database.add_payment(PAYMENT)
    app = create_app(database, API_TOKEN, ("https://dashboard.example",), lambda: True)
    return TestClient(app)


def test_private_routes_reject_missing_and_invalid_tokens(tmp_path) -> None:
    client = make_client(tmp_path)
    for route in ("/api/status", "/api/payments", "/api/payments.csv"):
        assert client.get(route).status_code == 401
        assert client.get(route, headers={"Authorization": "Bearer invalid"}).status_code == 401
    assert client.get("/healthz").json() == {"status": "ok"}


def test_authorized_read_endpoints_and_initial_cursor(tmp_path) -> None:
    client = make_client(tmp_path)
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    status = client.get("/api/status", headers=headers)
    assert status.json() == {"telegram_connected": True}
    response = client.get("/api/payments", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["initial"] is True
    assert body["cursor"] == 1
    assert body["payments"][0]["announcement"] == "ទទួលបានប្រាក់ ប្រាំម៉ឺនរៀល"
    assert client.get("/api/payments.csv", headers=headers).status_code == 200


def test_cors_is_restricted_to_configured_dashboard(tmp_path) -> None:
    client = make_client(tmp_path)
    response = client.options(
        "/api/status",
        headers={
            "Origin": "https://dashboard.example",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://dashboard.example"
    denied = client.options(
        "/api/status",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert "access-control-allow-origin" not in denied.headers


def test_local_dashboard_serves_only_public_static_files(tmp_path) -> None:
    database = PaymentDatabase(tmp_path / "history.sqlite3")
    app = create_app(database, API_TOKEN, static_dir=Path(__file__).resolve().parents[1])
    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/styles.css").status_code == 200
    assert client.get("/app.js").status_code == 200
    assert client.get("/.env").status_code == 404
    assert client.get("/payment_history.sqlite3").status_code == 404
