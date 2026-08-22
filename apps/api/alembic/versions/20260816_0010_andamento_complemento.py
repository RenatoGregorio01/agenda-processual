"""add complemento and orgao on processo_andamentos

Revision ID: 20260816_0010
Revises: 20260814_0009
Create Date: 2026-08-16

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260816_0010"
down_revision: str | None = "20260814_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "processo_andamentos",
        sa.Column("complemento", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "processo_andamentos",
        sa.Column("orgao", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("processo_andamentos", "orgao")
    op.drop_column("processo_andamentos", "complemento")
