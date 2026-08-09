"""create feriados table

Revision ID: 20260809_0002
Revises: 20260809_0001
Create Date: 2026-08-09

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260809_0002"
down_revision: str | None = "20260809_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "feriados",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feriados_data", "feriados", ["data"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_feriados_data", table_name="feriados")
    op.drop_table("feriados")
