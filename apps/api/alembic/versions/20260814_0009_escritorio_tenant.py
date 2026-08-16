"""add escritorios and escritorio_id on root tables

Revision ID: 20260814_0009
Revises: 20260812_0008
Create Date: 2026-08-14

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260814_0009"
down_revision: str | None = "20260812_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ROOT_TABLES = (
    "users",
    "prazos",
    "processos",
    "convites",
    "feriados",
    "audit_logs",
    "alerta_envios",
)


def upgrade() -> None:
    op.create_table(
        "escritorios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_escritorios_slug", "escritorios", ["slug"], unique=True)

    op.execute(
        """
        INSERT INTO escritorios (id, nome, slug, criado_em)
        SELECT gen_random_uuid(), 'Escritório', 'escritorio', NOW()
        WHERE NOT EXISTS (SELECT 1 FROM escritorios WHERE slug = 'escritorio')
        """
    )

    for table in ROOT_TABLES:
        op.add_column(table, sa.Column("escritorio_id", sa.Uuid(), nullable=True))
        op.execute(
            f"""
            UPDATE {table}
            SET escritorio_id = (SELECT id FROM escritorios WHERE slug = 'escritorio' LIMIT 1)
            WHERE escritorio_id IS NULL
            """
        )
        op.alter_column(table, "escritorio_id", nullable=False)
        op.create_index(f"ix_{table}_escritorio_id", table, ["escritorio_id"])
        op.create_foreign_key(
            f"fk_{table}_escritorio",
            table,
            "escritorios",
            ["escritorio_id"],
            ["id"],
        )

    op.create_unique_constraint(
        "uq_user_escritorio_email",
        "users",
        ["escritorio_id", "email"],
    )

    op.drop_constraint("processos_numero_processo_key", "processos", type_="unique")
    op.create_unique_constraint(
        "uq_processo_escritorio_numero",
        "processos",
        ["escritorio_id", "numero_processo"],
    )

    op.drop_constraint("feriados_data_key", "feriados", type_="unique")
    op.create_unique_constraint(
        "uq_feriado_escritorio_data",
        "feriados",
        ["escritorio_id", "data"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_feriado_escritorio_data", "feriados", type_="unique")
    op.create_unique_constraint("feriados_data_key", "feriados", ["data"])

    op.drop_constraint("uq_processo_escritorio_numero", "processos", type_="unique")
    op.create_unique_constraint(
        "processos_numero_processo_key",
        "processos",
        ["numero_processo"],
    )

    op.drop_constraint("uq_user_escritorio_email", "users", type_="unique")

    for table in reversed(ROOT_TABLES):
        op.drop_constraint(f"fk_{table}_escritorio", table, type_="foreignkey")
        op.drop_index(f"ix_{table}_escritorio_id", table_name=table)
        op.drop_column(table, "escritorio_id")

    op.drop_index("ix_escritorios_slug", table_name="escritorios")
    op.drop_table("escritorios")
