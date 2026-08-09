"""create convites table

Revision ID: 20260809_0003
Revises: 20260809_0002
Create Date: 2026-08-09

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260809_0003"
down_revision: str | None = "20260809_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "convites",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("receber_alertas", sa.Boolean(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("invited_by_id", sa.Uuid(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_convites_email", "convites", ["email"], unique=False)
    op.create_index("ix_convites_role", "convites", ["role"], unique=False)
    op.create_index("ix_convites_token_hash", "convites", ["token_hash"], unique=True)
    op.create_index("ix_convites_expires_at", "convites", ["expires_at"], unique=False)
    op.create_index("ix_convites_used_at", "convites", ["used_at"], unique=False)
    op.create_index("ix_convites_invited_by_id", "convites", ["invited_by_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_convites_invited_by_id", table_name="convites")
    op.drop_index("ix_convites_used_at", table_name="convites")
    op.drop_index("ix_convites_expires_at", table_name="convites")
    op.drop_index("ix_convites_token_hash", table_name="convites")
    op.drop_index("ix_convites_role", table_name="convites")
    op.drop_index("ix_convites_email", table_name="convites")
    op.drop_table("convites")
