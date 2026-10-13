import sqlite3
from datetime import datetime, timedelta, timezone

from database import PaymentDatabase


PAYMENT = {
    "currency": "USD",
    "amount": "12.50",
    "customer_name": "Example Customer",
    "account_suffix": "844",
    "payment_method": "ABA KHQR",
    "bank_name": "Example Bank Plc",
    "merchant_name": "Example Shop",
    "payment_datetime": "Oct 04, 01:55 PM",
    "transaction_id": "100000000000001",
    "approval_code": "512666",
}


def test_transaction_ids_are_unique_and_persist_after_restart(tmp_path) -> None:
    path = tmp_path / "history.sqlite3"
    first_run = PaymentDatabase(path)
    assert first_run.add_payment(PAYMENT) is True
    assert first_run.add_payment(PAYMENT) is False

    restarted = PaymentDatabase(path)
    cursor, rows = restarted.latest()
    assert cursor == 1
    assert len(rows) == 1
    assert rows[0]["transaction_id"] == PAYMENT["transaction_id"]


def test_initial_snapshot_does_not_mark_history_as_new(tmp_path) -> None:
    database = PaymentDatabase(tmp_path / "history.sqlite3")
    database.add_payment(PAYMENT)
    cursor, existing = database.latest()
    assert existing[0]["transaction_id"] == PAYMENT["transaction_id"]
    assert database.after(cursor) == []

    newer = dict(PAYMENT, transaction_id="100000000000002", amount="25.00")
    assert database.add_payment(newer) is True
    payments = database.after(cursor)
    assert [payment["transaction_id"] for payment in payments] == [
        "100000000000002"
    ]


def test_csv_export_contains_headers_and_payment(tmp_path) -> None:
    database = PaymentDatabase(tmp_path / "history.sqlite3")
    database.add_payment(PAYMENT)
    exported = database.export_csv()
    assert "transaction_id" in exported
    assert PAYMENT["transaction_id"] in exported


def test_csv_export_escapes_formula_like_customer_values(tmp_path) -> None:
    database = PaymentDatabase(tmp_path / "history.sqlite3")
    unsafe = dict(PAYMENT, customer_name="=HYPERLINK(\"https://example.invalid\")")
    database.add_payment(unsafe)
    assert "'=HYPERLINK(" in database.export_csv()


def test_expired_payment_is_preserved_when_database_restarts(tmp_path) -> None:
    path = tmp_path / "history.sqlite3"
    database = PaymentDatabase(path, retention_days=1)
    database.add_payment(PAYMENT)
    old_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    with sqlite3.connect(path) as connection:
        connection.execute(
            "UPDATE payments SET received_at = ?", (old_date,)
        )

    restarted = PaymentDatabase(path, retention_days=1)
    _, rows = restarted.latest()
    assert len(rows) == 1
    assert rows[0]["transaction_id"] == PAYMENT["transaction_id"]


def test_retention_is_applied_when_a_payment_is_added(tmp_path) -> None:
    path = tmp_path / "history.sqlite3"
    database = PaymentDatabase(path, retention_days=1)
    database.add_payment(PAYMENT)
    old_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE payments SET received_at = ?", (old_date,))

    newer = dict(PAYMENT, transaction_id="100000000000003")
    assert database.add_payment(newer) is True
    _, rows = database.latest()
    assert [row["transaction_id"] for row in rows] == [newer["transaction_id"]]


def test_existing_database_is_migrated_without_losing_payment_rows(tmp_path) -> None:
    path = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency TEXT NOT NULL,
                amount TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                account_suffix TEXT,
                payment_method TEXT NOT NULL,
                bank_name TEXT,
                merchant_name TEXT NOT NULL,
                payment_datetime TEXT NOT NULL,
                transaction_id TEXT NOT NULL UNIQUE,
                approval_code TEXT NOT NULL,
                received_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO payments (
                currency, amount, customer_name, account_suffix, payment_method,
                bank_name, merchant_name, payment_datetime, transaction_id,
                approval_code, received_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                PAYMENT["currency"],
                PAYMENT["amount"],
                PAYMENT["customer_name"],
                PAYMENT["account_suffix"],
                PAYMENT["payment_method"],
                PAYMENT["bank_name"],
                PAYMENT["merchant_name"],
                PAYMENT["payment_datetime"],
                PAYMENT["transaction_id"],
                PAYMENT["approval_code"],
                "2026-10-13T00:00:00+00:00",
            ),
        )

    database = PaymentDatabase(path)
    _, rows = database.latest(limit=1)
    assert len(rows) == 1
    assert rows[0]["transaction_id"] == PAYMENT["transaction_id"]
    assert rows[0]["payment_status"] is None
    assert database.add_payment(PAYMENT) is False


def test_telegram_source_ids_prevent_duplicate_messages_after_restart(tmp_path) -> None:
    path = tmp_path / "history.sqlite3"
    database = PaymentDatabase(path)
    assert database.add_payment(
        PAYMENT,
        source_chat_id="-1001234567890",
        source_message_id=42,
    )
    assert not database.add_payment(
        dict(PAYMENT, transaction_id="100000000000002"),
        source_chat_id="-1001234567890",
        source_message_id=42,
    )

    restarted = PaymentDatabase(path)
    assert not restarted.add_payment(
        dict(PAYMENT, transaction_id="100000000000003"),
        source_chat_id="-1001234567890",
        source_message_id=42,
    )
    _, rows = restarted.latest()
    assert len(rows) == 1
    assert rows[0]["source_chat_id"] == "-1001234567890"
    assert rows[0]["source_message_id"] == "42"
