"""Alembic migration environment — async SQLAlchemy.

This env.py supports Railway Postgres via asyncpg.  It reads DATABASE_URL
from the same pydantic-settings config used by the application so that the
URL coercion (postgres:// → postgresql+asyncpg://) is applied automatically.
"""

from __future__ import annotations

import asyncio
import os
# ── Import application metadata ────────────────────────────────────────────
# Import models so their tables are registered on Base.metadata before
# Alembic autogenerates or applies migrations.
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Ensure the monorepo root is on PYTHONPATH when running alembic from
# apps/backend/ so that `from apps.backend.*` imports work.
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import apps.backend.models.artifact  # noqa: F401, E402
# Import all models to populate Base.metadata
import apps.backend.models.lead  # noqa: F401, E402
import apps.backend.models.scrape_job  # noqa: F401, E402
from apps.backend.core.config import settings  # noqa: E402
from apps.backend.core.database import Base  # noqa: E402

# ── Alembic config object ──────────────────────────────────────────────────
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL without requiring a live DB connection — useful for
    generating migration scripts for review before applying.
    """
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using async engine."""
    connectable = create_async_engine(settings.DATABASE_URL, echo=False)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
