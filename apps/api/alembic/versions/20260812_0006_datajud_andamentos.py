"""create processo_andamentos and datajud columns

Revision ID: 20260812_0006
Revises: 20260810_0005
Create Date: 2026-08-12

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260812_0006"
down_revision: str | None = "20260810_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("processos", sa.Column("datajud_status", sa.String(length=40), nullable=True))
    op.add_column("processos", sa.Column("datajud_sincronizado_em", sa.DateTime(), nullable=True))
    op.add_column("processos", sa.Column("datajud_tribunal", sa.String(length=20), nullable=True))
    op.add_column("processos", sa.Column("datajud_grau", sa.String(length=20), nullable=True))
    op.add_column("processos", sa.Column("datajud_classe", sa.String(length=255), nullable=True))
    op.add_column("processos", sa.Column("datajud_orgao", sa.String(length=255), nullable=True))
    op.add_column("processos", sa.Column("datajud_mensagem", sa.String(length=500), nullable=True))
    op.create_table(
        "processo_andamentos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("processo_id", sa.Uuid(), nullable=False),
        sa.Column("data_hora", sa.DateTime(), nullable=True),
        sa.Column("codigo", sa.Integer(), nullable=True),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["processo_id"], ["processos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_processo_andamentos_processo_id",
        "processo_andamentos",
        ["processo_id"],
        unique=False,
    )
    op.create_index(
        "ix_processo_andamentos_data_hora",
        "processo_andamentos",
        ["data_hora"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_processo_andamentos_data_hora", table_name="processo_andamentos")
    op.drop_index("ix_processo_andamentos_processo_id", table_name="processo_andamentos")
    op.drop_table("processo_andamentos")
    op.drop_column("processos", "datajud_mensagem")
    op.drop_column("processos", "datajud_orgao")
    op.drop_column("processos", "datajud_classe")
    op.drop_column("processos", "datajud_grau")
    op.drop_column("processos", "datajud_tribunal")
    op.drop_column("processos", "datajud_sincronizado_em")
    op.drop_column("processos", "datajud_status")
