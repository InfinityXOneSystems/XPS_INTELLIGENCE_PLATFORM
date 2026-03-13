import re
from typing import Optional

import structlog

logger = structlog.get_logger(__name__)


def validate_email(value: str) -> Optional[str]:
    """Return normalized email or None if invalid."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if value and re.match(pattern, value.strip()):
        return value.strip().lower()
    return None


def validate_phone(value: str) -> Optional[str]:
    """Return normalized phone (E.164) or None if invalid."""
    try:
        import phonenumbers
        parsed = phonenumbers.parse(value, "US")
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        pass
    return None


def validate_url(value: str) -> Optional[str]:
    """Return URL if valid, None otherwise."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if value and re.match(pattern, value.strip()):
        return value.strip()
    return None


def validate_idempotency_key(key: str) -> bool:
    """Validate idempotency key format."""
    return bool(key and len(key) <= 255 and re.match(r'^[a-zA-Z0-9:_\-\.]+$', key))
