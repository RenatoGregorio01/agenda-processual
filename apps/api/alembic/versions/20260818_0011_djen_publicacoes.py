"""create djen_publicacoes and processo.djen_sincronizado_em

Revision ID: 20260818_0011
Revises: 20260816_0010
Create Date: 2026-08-18

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260818_0011"
down_revision: str | None = "20260816_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "processos",
        sa.Column("djen_sincronizado_em", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "djen_publicacoes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("escritorio_id", sa.Uuid(), nullable=False),
        sa.Column("processo_id", sa.Uuid(), nullable=True),
        sa.Column("prazo_id", sa.Uuid(), nullable=True),
        sa.Column("djen_id", sa.String(length=40), nullable=False),
        sa.Column("hash", sa.String(length=80), nullable=True),
        sa.Column("numero_processo", sa.String(length=64), nullable=False),
        sa.Column("numero_processo_digitos", sa.String(length=20), nullable=False),
        sa.Column("tribunal", sa.String(length=20), nullable=True),
        sa.Column("tipo_comunicacao", sa.String(length=80), nullable=False),
        sa.Column("tipo_documento", sa.String(length=80), nullable=True),
        sa.Column("orgao", sa.String(length=255), nullable=True),
        sa.Column("data_disponibilizacao", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("motivo_cancelamento", sa.String(length=500), nullable=True),
        sa.Column("sincronizado_em", sa.DateTime(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["escritorio_id"], ["escritorios.id"]),
        sa.ForeignKeyConstraint(["processo_id"], ["processos.id"]),
        sa.ForeignKeyConstraint(["prazo_id"], ["prazos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("escritorio_id", "djen_id", name="uq_djen_escritorio_id"),
    )
    op.create_index("ix_djen_publicacoes_escritorio_id", "djen_publicacoes", ["escritorio_id"])
    op.create_index("ix_djen_publicacoes_processo_id", "djen_publicacoes", ["processo_id"])
    op.create_index("ix_djen_publicacoes_prazo_id", "djen_publicacoes", ["prazo_id"])
    op.create_index("ix_djen_publicacoes_djen_id", "djen_publicacoes", ["djen_id"])
    op.create_index("ix_djen_publicacoes_numero_processo", "djen_publicacoes", ["numero_processo"])
    op.create_index(
        "ix_djen_publicacoes_numero_processo_digitos",
        "djen_publicacoes",
        ["numero_processo_digitos"],
    )
    op.create_index(
        "ix_djen_publicacoes_data_disponibilizacao",
        "djen_publicacoes",
        ["data_disponibilizacao"],
    )
    op.create_index("ix_djen_publicacoes_status", "djen_publicacoes", ["status"])


def downgrade() -> None:
    op.drop_index("ix_djen_publicacoes_status", table_name="djen_publicacoes")
    op.drop_index("ix_djen_publicacoes_data_disponibilizacao", table_name="djen_publicacoes")
    op.drop_index("ix_djen_publicacoes_numero_processo_digitos", table_name="djen_publicacoes")
    op.drop_index("ix_djen_publicacoes_numero_processo", table_name="djen_publicacoes")
    op.drop_index("ix_djen_publicacoes_djen_id", table_name="djen_publicacoes")
    op.drop_index("ix_djen_publicacoes_prazo_id", table_name="djen_publicacoes")
    op.drop_index("ix_djen_publicacoes_processo_id", table_name="djen_publicacoes")
    op.drop_index("ix_djen_publicacoes_escritorio_id", table_name="djen_publicacoes")
    op.drop_table("djen_publicacoes")
    op.drop_column("processos", "djen_sincronizado_em")
