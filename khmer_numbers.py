"""Convert payment amounts into Khmer words without external services."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

_DIGITS = (
    "សូន្យ",
    "មួយ",
    "ពីរ",
    "បី",
    "បួន",
    "ប្រាំ",
    "ប្រាំមួយ",
    "ប្រាំពីរ",
    "ប្រាំបី",
    "ប្រាំបួន",
)
_TENS = {
    10: "ដប់",
    20: "ម្ភៃ",
    30: "សាមសិប",
    40: "សែសិប",
    50: "ហាសិប",
    60: "ហុកសិប",
    70: "ចិតសិប",
    80: "ប៉ែតសិប",
    90: "កៅសិប",
}
_SCALES = ((100_000, "សែន"), (10_000, "ម៉ឺន"), (1_000, "ពាន់"), (100, "រយ"))
_MAX_AMOUNT = 10**18


def integer_to_khmer_words(value: int) -> str:
    """Spell a non-negative integer, including recursively grouped millions."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("The amount must be a non-negative whole number.")
    if value >= _MAX_AMOUNT:
        raise ValueError("The amount is too large to convert safely.")
    if value < 10:
        return _DIGITS[value]
    if value < 100:
        tens, ones = divmod(value, 10)
        prefix = _TENS[tens * 10]
        return prefix if ones == 0 else f"{prefix}{_DIGITS[ones]}"

    if value >= 1_000_000:
        millions, remainder = divmod(value, 1_000_000)
        result = f"{integer_to_khmer_words(millions)}លាន"
        return result if remainder == 0 else f"{result} {integer_to_khmer_words(remainder)}"

    parts: list[str] = []
    remainder = value
    for scale, name in _SCALES:
        quantity, remainder = divmod(remainder, scale)
        if quantity:
            parts.append(f"{integer_to_khmer_words(quantity)}{name}")
    if remainder:
        parts.append(integer_to_khmer_words(remainder))
    return " ".join(parts)


def amount_to_khmer(amount: str | int | float | Decimal, currency: str) -> str:
    """Convert USD/KHR into spoken Khmer with dollars, cents, or riel."""
    currency = currency.upper()
    if currency not in {"USD", "KHR"}:
        raise ValueError("Currency must be USD or KHR.")
    try:
        value = Decimal(str(amount).replace(",", ""))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Amount must be a valid non-negative number.") from exc
    if not value.is_finite() or value < 0:
        raise ValueError("Amount must be a valid non-negative number.")
    if currency == "USD" and value.as_tuple().exponent < -2:
        raise ValueError("USD amounts may have at most two decimal places.")
    if currency == "KHR":
        if value != value.to_integral_value():
            raise ValueError("Riel amounts must be whole numbers.")
        return f"{integer_to_khmer_words(int(value))}រៀល"

    cents_total = int((value * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    dollars, cents = divmod(cents_total, 100)
    parts = []
    if dollars:
        parts.append(f"{integer_to_khmer_words(dollars)}ដុល្លារ")
    if cents:
        parts.append(f"{integer_to_khmer_words(cents)}សេន")
    return " និង".join(parts) if parts else "សូន្យដុល្លារ"


def announcement_text(amount: str | int | float | Decimal, currency: str) -> str:
    """Build the full spoken notification sentence for a payment."""
    return f"ទទួលបានប្រាក់ {amount_to_khmer(amount, currency)}"
