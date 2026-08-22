"""add eh_advogado, oab_numero, oab_uf to users and convites

Revision ID: 20260822_0013
Revises: 20260821_0012
Create Date: 2026-08-22

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260822_0013"
down_revision: str | None = "20260821_0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("eh_advogado", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("users", sa.Column("oab_numero", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("oab_uf", sa.String(length=2), nullable=True))

    op.add_column(
        "convites",
        sa.Column("eh_advogado", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("convites", sa.Column("oab_numero", sa.String(length=20), nullable=True))
    op.add_column("convites", sa.Column("oab_uf", sa.String(length=2), nullable=True))


def downgrade() -> None:
    op.drop_column("convites", "oab_uf")
    op.drop_column("convites", "oab_numero")
    op.drop_column("convites", "eh_advogado")
    op.drop_column("users", "oab_uf")
    op.drop_column("users", "oab_numero")
    op.drop_column("users", "eh_advogado")
