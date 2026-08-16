"""add processo values to auditaction enum

Revision ID: 20260812_0007
Revises: 20260812_0006
Create Date: 2026-08-12

"""

from collections.abc import Sequence

from alembic import op
from app.models.audit_log import AuditAction

revision: str = "20260812_0007"
down_revision: str | None = "20260812_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for value in AuditAction:
        op.execute(f"ALTER TYPE auditaction ADD VALUE IF NOT EXISTS '{value.value}'")


def downgrade() -> None:
    # Postgres não remove valores de enum com segurança.
    pass
