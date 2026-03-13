from typing import Dict, Set

import structlog

logger = structlog.get_logger(__name__)


class CapabilityError(Exception):
    """Raised when a required capability is not granted."""
    pass


CAPABILITY_REGISTRY: Dict[str, str] = {
    "network_external": "Access external network URLs",
    "network_restricted": "Access only allowlisted URLs",
    "filesystem_read": "Read from filesystem",
    "filesystem_write": "Write to filesystem",
    "db_read": "Read from database",
    "db_write": "Write to database",
    "llm_invoke": "Invoke LLM providers",
    "scrape_execute": "Execute web scraping",
    "sandbox_execute": "Execute code in sandbox",
}

DEFAULT_SANDBOX_CAPS: Set[str] = {
    "network_restricted",
    "db_read",
    "db_write",
}


def check_capability(required: str, granted: Set[str]) -> bool:
    """Check if a required capability is in the granted set."""
    return required in granted


def require_capability(required: str, granted: Set[str]) -> None:
    """Assert a capability is granted, raising CapabilityError if not."""
    if not check_capability(required, granted):
        raise CapabilityError(
            f"Capability '{required}' is required but not granted. "
            f"Granted capabilities: {sorted(granted)}"
        )


def validate_capability_set(caps: Set[str]) -> Set[str]:
    """Return only known capabilities, logging unknown ones."""
    known = set(CAPABILITY_REGISTRY.keys())
    unknown = caps - known
    if unknown:
        logger.warning("unknown_capabilities", unknown=sorted(unknown))
    return caps & known
