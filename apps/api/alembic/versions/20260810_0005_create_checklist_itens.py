"""create checklist_itens table

Revision ID: 20260810_0005
Revises: 20260810_0004
Create Date: 2026-08-10

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260810_0005"
down_revision: str | None = "20260810_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "checklist_itens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("prazo_id", sa.Uuid(), nullable=False),
        sa.Column("texto", sa.String(length=255), nullable=False),
        sa.Column("concluido", sa.Boolean(), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["prazo_id"], ["prazos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_checklist_itens_prazo_id", "checklist_itens", ["prazo_id"], unique=False)
    op.create_index("ix_checklist_itens_concluido", "checklist_itens", ["concluido"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_checklist_itens_concluido", table_name="checklist_itens")
    op.drop_index("ix_checklist_itens_prazo_id", table_name="checklist_itens")
    op.drop_table("checklist_itens")
