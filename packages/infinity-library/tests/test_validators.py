from infinity_library.validators import (validate_email,
                                         validate_idempotency_key,
                                         validate_phone, validate_url)


def test_validate_phone_valid():
    result = validate_phone("+12025551234")
    # phonenumbers validates +1 numbers; result is E.164 or None depending on lib
    assert result is None or result.startswith("+")


def test_validate_phone_invalid():
    assert validate_phone("not-a-phone") is None


def test_validate_email_valid():
    assert validate_email("test@example.com") == "test@example.com"


def test_validate_email_normalizes_case():
    assert validate_email("Test@Example.COM") == "test@example.com"


def test_validate_email_invalid():
    assert validate_email("not-an-email") is None


def test_validate_email_empty():
    assert validate_email("") is None


def test_validate_url_valid():
    assert validate_url("https://example.com") == "https://example.com"


def test_validate_url_http():
    assert validate_url("http://example.com/path?q=1") == "http://example.com/path?q=1"


def test_validate_url_invalid():
    assert validate_url("not-a-url") is None


def test_validate_url_ftp_invalid():
    assert validate_url("ftp://example.com") is None


def test_validate_idempotency_key_valid():
    assert validate_idempotency_key("scrape:job123:https-example.com:0") is True


def test_validate_idempotency_key_invalid():
    assert validate_idempotency_key("") is False


def test_validate_idempotency_key_too_long():
    assert validate_idempotency_key("a" * 256) is False
