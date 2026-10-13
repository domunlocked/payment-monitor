from parser import parse_payment_message


def test_parses_usd_and_optional_bank_details() -> None:
    message = (
        "$12.50 paid by TEST CUSTOMER (*844) on Oct 04, 01:55 PM via ABA KHQR "
        "(Example Bank (Cambodia) Plc) at Example Shop. Trx. ID: 100000000000001, APV: 512666."
    )
    payment = parse_payment_message(message)
    assert payment is not None
    assert payment.to_dict() == {
        "currency": "USD",
        "amount": "12.50",
        "payment_status": "Paid",
        "customer_name": "TEST CUSTOMER",
        "account_suffix": "844",
        "payment_method": "ABA KHQR",
        "bank_name": "Example Bank (Cambodia) Plc",
        "merchant_name": "Example Shop",
        "payment_datetime": "Oct 04, 01:55 PM",
        "transaction_id": "100000000000001",
        "approval_code": "512666",
    }


def test_parses_khr_commas_case_and_missing_optional_bank() -> None:
    message = (
        "  ៛ 50,000 PAID BY Example Customer (*721) on Oct 04, 01:36 PM "
        "via ABA PAY at Example Shop. Trx. ID: 100000000000002, APV: 211408.  "
    )
    payment = parse_payment_message(message)
    assert payment is not None
    assert payment.currency == "KHR"
    assert payment.amount == "50000"
    assert payment.payment_status == "Paid"
    assert payment.customer_name == "Example Customer"
    assert payment.account_suffix == "721"
    assert payment.bank_name is None
    assert payment.payment_method == "ABA PAY"


def test_parses_missing_account_suffix_and_usd_decimal() -> None:
    message = (
        "$10.00 paid by Example Buyer on Oct 04, 01:39 PM via ABA PAY "
        "at Example Shop. Trx. ID: 100000000000003, APV: 926687"
    )
    payment = parse_payment_message(message)
    assert payment is not None
    assert payment.currency == "USD"
    assert payment.amount == "10.00"
    assert payment.account_suffix is None


def test_parses_small_riel_amount_with_commas() -> None:
    message = (
        "៛5,000 paid by Example Buyer (*092) on Oct 04, 01:57 PM via ABA PAY "
        "at Example Shop. Trx. ID: 100000000000007, APV: 731882."
    )
    payment = parse_payment_message(message)
    assert payment is not None
    assert payment.currency == "KHR"
    assert payment.amount == "5000"
    assert payment.transaction_id == "100000000000007"


def test_ignores_incomplete_invalid_and_non_payment_messages() -> None:
    invalid = (
        "hello",
        "$0.00 paid by Example Customer on Oct 04 via ABA PAY at Example Shop. "
        "Trx. ID: 100000000000004, APV: 123456",
        "៛1.50 paid by Example Customer on Oct 04 via ABA PAY at Example Shop. "
        "Trx. ID: 100000000000005, APV: 123456",
        "$1,00 paid by Example Customer on Oct 04 via ABA PAY at Example Shop. "
        "Trx. ID: 100000000000006, APV: 123456",
        "$15 paid by Example Customer on Oct 04 via ABA PAY at Example Shop.",
    )
    for message in invalid:
        assert parse_payment_message(message) is None
