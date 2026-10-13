"""SQLite payment history with transaction-ID deduplication and retention."""

import csv
import io
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_COLUMNS = (
    "id, currency, amount, customer_name, account_suffix, payment_method, "
    "bank_name, merchant_name, payment_datetime, transaction_id, approval_code, "
    "received_at"
)


class PaymentDatabase:
    def __init__(self, path: str | Path, retention_days: int = 365) -> None:
        self.path = Path(path)
        self.retention_days = retention_days
        if retention_days < 1:
            raise ValueError("retention_days must be at least 1.")
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency TEXT NOT NULL CHECK(currency IN ('USD', 'KHR')),
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
                "CREATE INDEX IF NOT EXISTS idx_payments_received_at "
                "ON payments(received_at)"
            )
            cutoff = (
                datetime.now(timezone.utc) - timedelta(days=self.retention_days)
            ).isoformat(timespec="seconds")
            connection.execute("DELETE FROM payments WHERE received_at < ?", (cutoff,))

    def add_payment(self, payment: dict[str, Any]) -> bool:
        """Insert one payment, returning False if its transaction ID already exists."""
        received_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        values = {key: payment.get(key) for key in (
            "currency", "amount", "customer_name", "account_suffix",
            "payment_method", "bank_name", "merchant_name", "payment_datetime",
            "transaction_id", "approval_code",
        )}
        if values["currency"] not in {"USD", "KHR"} or not values["transaction_id"]:
            raise ValueError("A valid currency and transaction ID are required.")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO payments (
                    currency, amount, customer_name, account_suffix, payment_method,
                    bank_name, merchant_name, payment_datetime, transaction_id,
                    approval_code, received_at
                ) VALUES (
                    :currency, :amount, :customer_name, :account_suffix,
                    :payment_method, :bank_name, :merchant_name, :payment_datetime,
                    :transaction_id, :approval_code, :received_at
                )
                """,
                {**values, "received_at": received_at},
            )
            inserted = cursor.rowcount == 1
            cutoff = (
                datetime.now(timezone.utc) - timedelta(days=self.retention_days)
            ).isoformat(timespec="seconds")
            connection.execute("DELETE FROM payments WHERE received_at < ?", (cutoff,))
        return inserted

    def latest(self, limit: int = 50) -> tuple[int, list[dict[str, Any]]]:
        with self._connect() as connection:
            connection.execute("BEGIN")
            watermark = connection.execute(
                "SELECT COALESCE(MAX(id), 0) FROM payments"
            ).fetchone()[0]
            rows = connection.execute(
                f"SELECT {_COLUMNS} FROM payments ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return watermark, [dict(row) for row in reversed(rows)]

    def after(self, cursor: int, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT {_COLUMNS} FROM payments WHERE id > ? ORDER BY id LIMIT ?",
                (cursor, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def export_csv(self) -> str:
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT {_COLUMNS} FROM payments ORDER BY id DESC"
            ).fetchall()
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        columns = tuple(column.strip() for column in _COLUMNS.split(","))
        writer.writerow(columns)
        for row in rows:
            values = []
            for value in row:
                if isinstance(value, str) and value.lstrip(" \t\r\n")[:1] in {"=", "+", "-", "@"}:
                    value = f"'{value}"
                values.append(value)
            writer.writerow(values)
        return "\ufeff" + output.getvalue()
