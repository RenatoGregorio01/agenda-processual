"""add DJEN historical queue and structured triage

Revision ID: 20260905_0018
Revises: 20260905_0017
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260905_0018"
down_revision: str | None = "20260905_0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "djen_publicacoes",
        sa.Column("classificacao_ato", sa.String(30), nullable=False, server_default="outro"),
    )
    op.add_column(
        "djen_publicacoes",
        sa.Column("confianca_prazo", sa.String(20), nullable=False, server_default="nenhuma"),
    )
    op.create_index(
        "ix_djen_publicacoes_classificacao_ato", "djen_publicacoes", ["classificacao_ato"]
    )
    op.create_index(
        "ix_djen_publicacoes_confianca_prazo", "djen_publicacoes", ["confianca_prazo"]
    )
    op.create_table(
        "djen_sync_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("escritorio_id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=True),
        sa.Column("numero_oab", sa.String(20), nullable=False),
        sa.Column("uf_oab", sa.String(2), nullable=False),
        sa.Column("data_inicio", sa.Date(), nullable=False),
        sa.Column("data_fim", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("publicacoes_criadas", sa.Integer(), nullable=False),
        sa.Column("mensagem_erro", sa.String(500), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("iniciado_em", sa.DateTime(), nullable=True),
        sa.Column("concluido_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["escritorio_id"], ["escritorios.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    columns = (
        "escritorio_id",
        "usuario_id",
        "numero_oab",
        "uf_oab",
        "data_inicio",
        "data_fim",
        "status",
    )
    for column in columns:
        op.create_index(f"ix_djen_sync_jobs_{column}", "djen_sync_jobs", [column])


def downgrade() -> None:
    columns = (
        "status",
        "data_fim",
        "data_inicio",
        "uf_oab",
        "numero_oab",
        "usuario_id",
        "escritorio_id",
    )
    for column in columns:
        op.drop_index(f"ix_djen_sync_jobs_{column}", table_name="djen_sync_jobs")
    op.drop_table("djen_sync_jobs")
    op.drop_index("ix_djen_publicacoes_confianca_prazo", table_name="djen_publicacoes")
    op.drop_index("ix_djen_publicacoes_classificacao_ato", table_name="djen_publicacoes")
    op.drop_column("djen_publicacoes", "confianca_prazo")
    op.drop_column("djen_publicacoes", "classificacao_ato")
