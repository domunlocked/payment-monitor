import pytest

from khmer_numbers import amount_to_khmer, announcement_text, integer_to_khmer_words


@pytest.mark.parametrize(
    ("amount", "currency", "expected"),
    [
        ("50000", "KHR", "ប្រាំម៉ឺនរៀល"),
        ("5000", "KHR", "ប្រាំពាន់រៀល"),
        ("0", "KHR", "សូន្យរៀល"),
        ("100000", "KHR", "មួយសែនរៀល"),
        ("1000000", "KHR", "មួយលានរៀល"),
        ("10000", "USD", "មួយម៉ឺនដុល្លារ"),
        ("12.50", "USD", "ដប់ពីរដុល្លារ និងហាសិបសេន"),
        ("10.05", "USD", "ដប់ដុល្លារ និងប្រាំសេន"),
        ("10.00", "USD", "ដប់ដុល្លារ"),
        ("0.50", "USD", "ហាសិបសេន"),
        ("0", "USD", "សូន្យដុល្លារ"),
        ("100.01", "USD", "មួយរយដុល្លារ និងមួយសេន"),
    ],
)
def test_amount_to_khmer(amount: str, currency: str, expected: str) -> None:
    assert amount_to_khmer(amount, currency) == expected


def test_complete_announcement_sentence() -> None:
    assert announcement_text(50_000, "KHR") == "ទទួលបានប្រាក់ ប្រាំម៉ឺនរៀល"


@pytest.mark.parametrize("value", [-1, 10**18])
def test_rejects_unsupported_integers(value: int) -> None:
    with pytest.raises(ValueError):
        integer_to_khmer_words(value)


@pytest.mark.parametrize(
    ("amount", "currency"),
    [
        ("-1", "USD"),
        ("NaN", "USD"),
        ("Infinity", "KHR"),
        ("1.5", "KHR"),
        ("1.001", "USD"),
        ("5", "EUR"),
    ],
)
def test_rejects_invalid_amounts(amount: str, currency: str) -> None:
    with pytest.raises(ValueError):
        amount_to_khmer(amount, currency)
