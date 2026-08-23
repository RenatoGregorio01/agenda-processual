"""create password reset tokens

Revision ID: 20260823_0015
Revises: 20260822_0014
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260823_0015"
down_revision: str | None = "20260822_0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "password_resets",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["contas.id"]),
    )
    op.create_index("ix_password_resets_account_id", "password_resets", ["account_id"])
    op.create_index("ix_password_resets_token_hash", "password_resets", ["token_hash"])
    op.create_index("ix_password_resets_expires_at", "password_resets", ["expires_at"])
    op.create_index("ix_password_resets_used_at", "password_resets", ["used_at"])


def downgrade() -> None:
    op.drop_table("password_resets")
