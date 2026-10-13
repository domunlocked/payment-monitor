"""Parse incoming ABA PayWay group notifications without network access."""

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
import re

_PAYMENT = re.compile(
    r"""
    ^\s*
    (?P<symbol>៛|\$)\s*
    (?P<amount>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?)
    \s+paid\s+by\s+
    (?P<customer>.+?)
    (?:\s+\(\s*\*(?P<suffix>\d+)\s*\))?
    \s+on\s+(?P<date>.+?)
    \s+via\s+(?P<method>.+?)
    (?:\s+\((?P<bank>[^()\r\n]*(?:\([^()\r\n]*\)[^()\r\n]*)*)\))?
    \s+at\s+(?P<merchant>.+?)
    [,.]?\s+Trx\.\s*ID\s*:\s*(?P<trx>[A-Za-z0-9_-]+)
    \s*,?\s*APV\s*:\s*(?P<apv>[A-Za-z0-9_-]+)
    \s*[.!]?\s*$
    """,
    re.IGNORECASE | re.VERBOSE | re.DOTALL,
)


@dataclass(frozen=True)
class Payment:
    currency: str
    amount: str
    customer_name: str
    account_suffix: str | None
    payment_method: str
    bank_name: str | None
    merchant_name: str
    payment_datetime: str
    transaction_id: str
    approval_code: str

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


def parse_payment_message(message: str) -> Payment | None:
    """Return parsed details only when a complete, plausible ABA payment matches."""
    match = _PAYMENT.fullmatch(message.strip())
    if not match:
        return None
    fields = match.groupdict()
    amount_text = fields["amount"].replace(",", "")
    try:
        amount = Decimal(amount_text)
    except InvalidOperation:
        return None
    if not amount.is_finite() or amount <= 0 or amount >= Decimal("1000000000000000000"):
        return None

    currency = "KHR" if fields["symbol"] == "៛" else "USD"
    if currency == "KHR" and amount != amount.to_integral_value():
        return None
    bank_text = fields["bank"].strip() if fields["bank"] else ""
    bank = bank_text or None
    payment_method = fields["method"].strip()
    customer_name = fields["customer"].strip()
    merchant_name = fields["merchant"].strip().rstrip(".,")
    date_text = fields["date"].strip().rstrip(".,")
    if not payment_method or not customer_name or not merchant_name or not date_text:
        return None
    return Payment(
        currency=currency,
        amount=format(amount, "f"),
        customer_name=customer_name,
        account_suffix=fields["suffix"],
        payment_method=payment_method,
        bank_name=bank,
        merchant_name=merchant_name,
        payment_datetime=date_text,
        transaction_id=fields["trx"],
        approval_code=fields["apv"],
    )
