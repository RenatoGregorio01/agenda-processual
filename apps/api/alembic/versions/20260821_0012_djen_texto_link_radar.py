"""add texto, link, nome_classe, destinatarios, dias_identificados to djen_publicacoes

Revision ID: 20260821_0012
Revises: 20260818_0011
Create Date: 2026-08-21

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260821_0012"
down_revision: str | None = "20260818_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "djen_publicacoes",
        sa.Column("nome_classe", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "djen_publicacoes",
        sa.Column("texto", sa.Text(), nullable=True),
    )
    op.add_column(
        "djen_publicacoes",
        sa.Column("link", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "djen_publicacoes",
        sa.Column("destinatarios", sa.Text(), nullable=True),
    )
    op.add_column(
        "djen_publicacoes",
        sa.Column("dias_identificados", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("djen_publicacoes", "dias_identificados")
    op.drop_column("djen_publicacoes", "destinatarios")
    op.drop_column("djen_publicacoes", "link")
    op.drop_column("djen_publicacoes", "texto")
    op.drop_column("djen_publicacoes", "nome_classe")
