# Agents — XPS Intelligence Platform

> **Status:** ⬜ Pending Phase 4 consolidation  
> **Sources:** Multiple repos (see below)

## Overview

All autonomous AI agents are consolidated here. Every agent implements the `BaseAgent` interface and uses the `MemoryAgent` for persistence.

## Agent Registry

| Agent | Source Repo | Phase | Status |
|-------|-------------|-------|--------|
| `shadow-scraper/` | `XPS_INTELLIGENCE_SYSTEM` | Phase 1 | ⬜ Pending |
| `intelligence/` | `XPS_INTELLIGENCE_SYSTEM` | Phase 1 | ⬜ Pending |
| `build/` | `QUANTUM-X-BUILD` | Phase 2 | ⬜ Pending |
| `admin/` | `VIZUAL-X-ADMIN-CONTROL-PLANE` | Phase 3 | ⬜ Pending |
| `construct-iq/` | `CONSTRUCT-IQ-360` | Phase 4 | ⬜ Pending |
| `memory/` | (new) | Phase 4 | ⬜ Pending |
| `conflict-resolver/` | (new) | Phase 4 | ⬜ Pending |
| `bot-updater/` | (new) | Phase 4 | ⬜ Pending |

## Base Agent Interface

```python
from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    """All agents must implement this interface."""

    @abstractmethod
    async def run(self) -> dict[str, Any]:
        """Execute the agent's primary task. Returns result dict."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the agent is operational."""

    async def save_memory(self, key: str, value: dict) -> None:
        """Persist state to Postgres via MemoryAgent."""

    async def load_memory(self, key: str) -> dict | None:
        """Load state from Postgres via MemoryAgent."""
```

## Shadow Scraper Rule (MANDATORY)

> **The Shadow Scraper MUST be used for all lead data.**  
> Fake, sample, or mock lead data is strictly prohibited.  
> No paid lead data APIs may be introduced.

## Human Gate

Agents will be consolidated in **Phases 1-4** after explicit human commands to begin consolidation.
