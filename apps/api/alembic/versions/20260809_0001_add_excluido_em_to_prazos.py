"""add excluido_em to prazos

Revision ID: 20260809_0001
Revises:
Create Date: 2026-08-09

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260809_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("prazos", sa.Column("excluido_em", sa.DateTime(), nullable=True))
    op.create_index("ix_prazos_excluido_em", "prazos", ["excluido_em"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_prazos_excluido_em", table_name="prazos")
    op.drop_column("prazos", "excluido_em")
