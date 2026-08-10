"""create processos and link prazos

Revision ID: 20260810_0004
Revises: 20260809_0003
Create Date: 2026-08-10

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260810_0004"
down_revision: str | None = "20260809_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "processos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("numero_processo", sa.String(length=64), nullable=False),
        sa.Column("cliente", sa.String(length=255), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_processos_numero_processo", "processos", ["numero_processo"], unique=True
    )
    op.add_column("prazos", sa.Column("processo_id", sa.Uuid(), nullable=True))
    op.create_index("ix_prazos_processo_id", "prazos", ["processo_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_prazos_processo_id", table_name="prazos")
    op.drop_column("prazos", "processo_id")
    op.drop_index("ix_processos_numero_processo", table_name="processos")
    op.drop_table("processos")
