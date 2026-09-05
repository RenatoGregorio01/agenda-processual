"""mark processes discovered through DJEN

Revision ID: 20260905_0017
Revises: 20260823_0015
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260905_0017"
down_revision: str | None = "20260823_0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "processos",
        sa.Column("origem_cadastro", sa.String(length=20), nullable=False, server_default="manual"),
    )
    op.add_column(
        "processos",
        sa.Column("pendente_revisao", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_processos_pendente_revisao", "processos", ["pendente_revisao"])


def downgrade() -> None:
    op.drop_index("ix_processos_pendente_revisao", table_name="processos")
    op.drop_column("processos", "pendente_revisao")
    op.drop_column("processos", "origem_cadastro")
