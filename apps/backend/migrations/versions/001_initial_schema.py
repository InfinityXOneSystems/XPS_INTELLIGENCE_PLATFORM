"""Initial schema — leads, artifacts, scrape_jobs tables.

Revision ID: 001
Revises:
Create Date: 2026-03-14

This migration creates all application tables from scratch.
It is idempotent: tables that already exist (created via
Base.metadata.create_all during development) are left untouched.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = inspector.get_table_names()

    if "leads" not in existing:
        op.create_table(
            "leads",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                nullable=False,
            ),
            sa.Column("source_url", sa.String(2048), nullable=False),
            sa.Column("raw_data", sa.JSON(), nullable=False),
            sa.Column("normalized_data", sa.JSON(), nullable=True),
            sa.Column("score", sa.Float(), nullable=True),
            sa.Column("status", sa.String(32), nullable=False, index=True),
            sa.Column(
                "idempotency_key",
                sa.String(255),
                unique=True,
                nullable=False,
                index=True,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )

    if "artifacts" not in existing:
        op.create_table(
            "artifacts",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                nullable=False,
            ),
            sa.Column("artifact_type", sa.String(64), nullable=False, index=True),
            sa.Column("title", sa.String(512), nullable=False),
            sa.Column("content", sa.JSON(), nullable=False),
            sa.Column("storage_url", sa.String(2048), nullable=True),
            sa.Column("job_id", sa.String(255), nullable=True, index=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )

    if "scrape_jobs" not in existing:
        op.create_table(
            "scrape_jobs",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                nullable=False,
            ),
            sa.Column("target_url", sa.String(2048), nullable=False),
            sa.Column("status", sa.String(32), nullable=False, index=True),
            sa.Column(
                "idempotency_key",
                sa.String(255),
                unique=True,
                nullable=False,
                index=True,
            ),
            sa.Column("result_count", sa.Integer(), nullable=False, default=0),
            sa.Column("error", sa.String(2048), nullable=True),
            sa.Column("scheduled", sa.Boolean(), nullable=False, default=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )


def downgrade() -> None:
    op.drop_table("scrape_jobs")
    op.drop_table("artifacts")
    op.drop_table("leads")
