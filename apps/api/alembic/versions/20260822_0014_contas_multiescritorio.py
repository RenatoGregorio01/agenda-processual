"""add global accounts for multi-office access

Revision ID: 20260822_0014
Revises: 20260822_0013
"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "20260822_0014"
down_revision: str | None = "20260822_0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_key")
    op.create_table(
        "contas",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_contas_email", "contas", ["email"])
    op.add_column("users", sa.Column("account_id", sa.Uuid(), nullable=True))
    op.create_index("ix_users_account_id", "users", ["account_id"])
    op.create_foreign_key("fk_users_account_id", "users", "contas", ["account_id"], ["id"])

    bind = op.get_bind()
    users = bind.execute(
        sa.text("SELECT id, email, nome, hashed_password, ativo, criado_em, atualizado_em FROM users")
    ).mappings()
    for user in users:
        account_id = uuid4()
        bind.execute(
            sa.text(
                "INSERT INTO contas (id, email, nome, hashed_password, ativo, criado_em, atualizado_em) "
                "VALUES (:id, :email, :nome, :hashed_password, :ativo, :criado_em, :atualizado_em)"
            ),
            {"id": account_id, **dict(user)},
        )
        bind.execute(
            sa.text("UPDATE users SET account_id = :account_id WHERE id = :user_id"),
            {"account_id": account_id, "user_id": user["id"]},
        )


def downgrade() -> None:
    op.create_unique_constraint("users_email_key", "users", ["email"])
    op.drop_constraint("fk_users_account_id", "users", type_="foreignkey")
    op.drop_index("ix_users_account_id", table_name="users")
    op.drop_column("users", "account_id")
    op.drop_index("ix_contas_email", table_name="contas")
    op.drop_table("contas")
