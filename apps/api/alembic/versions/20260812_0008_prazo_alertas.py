"""create prazo_alertas and migrate alerta_envios to dias_antes

Revision ID: 20260812_0008
Revises: 20260812_0007
Create Date: 2026-08-12

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260812_0008"
down_revision: str | None = "20260812_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "prazo_alertas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("prazo_id", sa.Uuid(), nullable=False),
        sa.Column("dias_antes", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["prazo_id"], ["prazos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("prazo_id", "dias_antes", name="uq_prazo_alerta_prazo_dias"),
    )
    op.create_index("ix_prazo_alertas_prazo_id", "prazo_alertas", ["prazo_id"])
    op.create_index("ix_prazo_alertas_dias_antes", "prazo_alertas", ["dias_antes"])

    op.add_column("alerta_envios", sa.Column("dias_antes", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE alerta_envios SET dias_antes = CASE
          WHEN tipo::text IN ('3dias', 'dias_3') THEN 3
          WHEN tipo::text IN ('2dias', 'dias_2') THEN 2
          WHEN tipo::text IN ('1dia', 'dias_1') THEN 1
          ELSE 1
        END
        WHERE dias_antes IS NULL
        """
    )
    op.execute("ALTER TABLE alerta_envios ALTER COLUMN dias_antes SET NOT NULL")
    op.drop_constraint("uq_alerta_envio_prazo_tipo_email", "alerta_envios", type_="unique")
    op.drop_column("alerta_envios", "tipo")
    op.create_index("ix_alerta_envios_dias_antes", "alerta_envios", ["dias_antes"])
    op.create_unique_constraint(
        "uq_alerta_envio_prazo_dias_email",
        "alerta_envios",
        ["prazo_id", "dias_antes", "destinatario_email"],
    )

    op.execute(
        """
        INSERT INTO prazo_alertas (id, prazo_id, dias_antes, criado_em)
        SELECT gen_random_uuid(), id, 3, NOW() FROM prazos
        WHERE COALESCE(alerta_3_dias, false) = true
        """
    )
    op.execute(
        """
        INSERT INTO prazo_alertas (id, prazo_id, dias_antes, criado_em)
        SELECT gen_random_uuid(), id, 2, NOW() FROM prazos
        WHERE COALESCE(alerta_2_dias, false) = true
        """
    )
    op.execute(
        """
        INSERT INTO prazo_alertas (id, prazo_id, dias_antes, criado_em)
        SELECT gen_random_uuid(), id, 1, NOW() FROM prazos
        WHERE COALESCE(alerta_1_dia, false) = true
        """
    )


def downgrade() -> None:
    op.drop_constraint("uq_alerta_envio_prazo_dias_email", "alerta_envios", type_="unique")
    op.drop_index("ix_alerta_envios_dias_antes", table_name="alerta_envios")
    op.add_column("alerta_envios", sa.Column("tipo", sa.String(length=20), nullable=True))
    op.execute(
        """
        UPDATE alerta_envios SET tipo = CASE
          WHEN dias_antes = 3 THEN '3dias'
          WHEN dias_antes = 2 THEN '2dias'
          ELSE '1dia'
        END
        """
    )
    op.drop_column("alerta_envios", "dias_antes")
    op.create_unique_constraint(
        "uq_alerta_envio_prazo_tipo_email",
        "alerta_envios",
        ["prazo_id", "tipo", "destinatario_email"],
    )
    op.drop_index("ix_prazo_alertas_dias_antes", table_name="prazo_alertas")
    op.drop_index("ix_prazo_alertas_prazo_id", table_name="prazo_alertas")
    op.drop_table("prazo_alertas")
