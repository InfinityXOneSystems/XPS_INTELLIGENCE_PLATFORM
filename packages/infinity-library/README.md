# infinity-library

Shared Python utilities for the XPS Intelligence Platform monorepo.

## Overview

`infinity-library` provides validators, structured logging helpers, and policy/capability
enforcement used across `apps/backend`, `apps/workers`, and any future Python service.

## Installation

From the repo root (editable install):
```bash
pip install -e packages/infinity-library
```

## Modules

### `infinity_library.validators`

| Function | Description |
|----------|-------------|
| `validate_email(value)` | Returns normalized lowercase email or `None` |
| `validate_phone(value)` | Returns E.164 phone string or `None` |
| `validate_url(value)` | Returns URL string if valid HTTP/HTTPS, else `None` |
| `validate_idempotency_key(key)` | Returns `True` if key matches safe charset, `False` otherwise |

### `infinity_library.logging`

| Function | Description |
|----------|-------------|
| `configure_logging(level, json_logs)` | Configure structlog globally |
| `get_logger(name)` | Return a bound structlog logger |

### `infinity_library.policy`

| Symbol | Description |
|--------|-------------|
| `CapabilityError` | Exception raised when a required capability is missing |
| `CAPABILITY_REGISTRY` | Dict of all known capability names → descriptions |
| `DEFAULT_SANDBOX_CAPS` | Default capability set for sandbox workers |
| `check_capability(required, granted)` | Returns `True/False` |
| `require_capability(required, granted)` | Raises `CapabilityError` if missing |
| `validate_capability_set(caps)` | Filters unknown capabilities and warns |

## Running Tests

```bash
cd packages/infinity-library
pytest
```
