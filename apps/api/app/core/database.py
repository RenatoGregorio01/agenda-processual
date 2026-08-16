from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings
from app.models import (  # noqa: F401
    AlertaEnvio,
    AuditAction,
    AuditLog,
    ChecklistItem,
    Convite,
    Escritorio,
    Feriado,
    Prazo,
    PrazoAlerta,
    Processo,
    ProcessoAndamento,
    User,
)

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        await conn.execute(
            text("ALTER TABLE prazos ADD COLUMN IF NOT EXISTS excluido_em TIMESTAMP NULL")
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_prazos_excluido_em ON prazos (excluido_em)"
            )
        )
        await conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20)")
        )
        await conn.execute(
            text(
                "UPDATE users SET role = CASE "
                "WHEN is_admin = true THEN 'admin' "
                "ELSE COALESCE(role, 'editor') END "
                "WHERE role IS NULL OR role = ''"
            )
        )
        await conn.execute(text("UPDATE users SET role = 'editor' WHERE role IS NULL"))
        await conn.execute(
            text("CREATE INDEX IF NOT EXISTS ix_users_role ON users (role)")
        )
        await conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS receber_alertas BOOLEAN "
                "DEFAULT TRUE NOT NULL"
            )
        )
        await conn.execute(
            text("ALTER TABLE prazos ADD COLUMN IF NOT EXISTS responsavel_id UUID NULL")
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_prazos_responsavel_id ON prazos (responsavel_id)"
            )
        )
        await conn.execute(
            text(
                "UPDATE prazos SET responsavel_id = users.id "
                "FROM users "
                "WHERE prazos.responsavel_id IS NULL "
                "AND lower(prazos.responsavel) = lower(users.nome)"
            )
        )
        await conn.execute(
            text(
                "UPDATE prazos SET responsavel_id = ("
                "SELECT id FROM users WHERE is_admin = true ORDER BY criado_em ASC LIMIT 1"
                ") "
                "WHERE responsavel_id IS NULL "
                "AND EXISTS (SELECT 1 FROM users WHERE is_admin = true)"
            )
        )
        await conn.execute(
            text("ALTER TABLE prazos ADD COLUMN IF NOT EXISTS processo_id UUID NULL")
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_prazos_processo_id ON prazos (processo_id)"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE processos ADD COLUMN IF NOT EXISTS datajud_status VARCHAR(40)"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE processos ADD COLUMN IF NOT EXISTS datajud_sincronizado_em TIMESTAMP"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE processos ADD COLUMN IF NOT EXISTS datajud_tribunal VARCHAR(20)"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE processos ADD COLUMN IF NOT EXISTS datajud_grau VARCHAR(20)"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE processos ADD COLUMN IF NOT EXISTS datajud_classe VARCHAR(255)"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE processos ADD COLUMN IF NOT EXISTS datajud_orgao VARCHAR(255)"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE processos ADD COLUMN IF NOT EXISTS datajud_mensagem VARCHAR(500)"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE processo_andamentos "
                "ADD COLUMN IF NOT EXISTS complemento VARCHAR(500)"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE processo_andamentos "
                "ADD COLUMN IF NOT EXISTS orgao VARCHAR(255)"
            )
        )
        if conn.dialect.name == "postgresql":
            for value in AuditAction:
                await conn.execute(
                    text(
                        "ALTER TYPE auditaction ADD VALUE IF NOT EXISTS "
                        f"'{value.value}'"
                    )
                )
            await conn.execute(
                text(
                    "ALTER TABLE alerta_envios ADD COLUMN IF NOT EXISTS dias_antes INTEGER"
                )
            )
            await conn.execute(
                text(
                    """
                    DO $$
                    BEGIN
                      IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'alerta_envios' AND column_name = 'tipo'
                      ) THEN
                        UPDATE alerta_envios SET dias_antes = CASE
                          WHEN tipo::text IN ('3dias', 'dias_3') THEN 3
                          WHEN tipo::text IN ('2dias', 'dias_2') THEN 2
                          WHEN tipo::text IN ('1dia', 'dias_1') THEN 1
                          ELSE COALESCE(dias_antes, 1)
                        END
                        WHERE dias_antes IS NULL;
                        ALTER TABLE alerta_envios
                          DROP CONSTRAINT IF EXISTS uq_alerta_envio_prazo_tipo_email;
                        ALTER TABLE alerta_envios DROP COLUMN tipo;
                      END IF;
                    END $$;
                    """
                )
            )
            await conn.execute(
                text(
                    "UPDATE alerta_envios SET dias_antes = 1 WHERE dias_antes IS NULL"
                )
            )
            await conn.execute(
                text(
                    """
                    DO $$
                    BEGIN
                      BEGIN
                        ALTER TABLE alerta_envios ALTER COLUMN dias_antes SET NOT NULL;
                      EXCEPTION
                        WHEN others THEN NULL;
                      END;
                    END $$;
                    """
                )
            )
            await conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_alerta_envio_prazo_dias_email "
                    "ON alerta_envios (prazo_id, dias_antes, destinatario_email)"
                )
            )
            await conn.execute(
                text(
                    """
                    DO $$
                    BEGIN
                      IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'prazos' AND column_name = 'alerta_3_dias'
                      ) THEN
                        INSERT INTO prazo_alertas (id, prazo_id, dias_antes, criado_em)
                        SELECT gen_random_uuid(), p.id, 3, NOW()
                        FROM prazos p
                        WHERE COALESCE(p.alerta_3_dias, false) = true
                        AND NOT EXISTS (
                          SELECT 1 FROM prazo_alertas pa
                          WHERE pa.prazo_id = p.id AND pa.dias_antes = 3
                        );
                      END IF;
                      IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'prazos' AND column_name = 'alerta_2_dias'
                      ) THEN
                        INSERT INTO prazo_alertas (id, prazo_id, dias_antes, criado_em)
                        SELECT gen_random_uuid(), p.id, 2, NOW()
                        FROM prazos p
                        WHERE COALESCE(p.alerta_2_dias, false) = true
                        AND NOT EXISTS (
                          SELECT 1 FROM prazo_alertas pa
                          WHERE pa.prazo_id = p.id AND pa.dias_antes = 2
                        );
                      END IF;
                      IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'prazos' AND column_name = 'alerta_1_dia'
                      ) THEN
                        INSERT INTO prazo_alertas (id, prazo_id, dias_antes, criado_em)
                        SELECT gen_random_uuid(), p.id, 1, NOW()
                        FROM prazos p
                        WHERE COALESCE(p.alerta_1_dia, false) = true
                        AND NOT EXISTS (
                          SELECT 1 FROM prazo_alertas pa
                          WHERE pa.prazo_id = p.id AND pa.dias_antes = 1
                        );
                      END IF;
                    END $$;
                    """
                )
            )
            await _ensure_escritorio_tenant(conn)


async def _ensure_escritorio_tenant(conn) -> None:
    # asyncpg exige cast explícito: reutilizar o mesmo param em INSERT/WHERE
    # sem tipo gera AmbiguousParameterError (text vs varchar).
    slug = settings.seed_escritorio_slug
    nome = settings.seed_escritorio_nome
    await conn.execute(
        text(
            """
            INSERT INTO escritorios (id, nome, slug, criado_em)
            SELECT gen_random_uuid(),
                   CAST(:nome AS VARCHAR(120)),
                   CAST(:slug AS VARCHAR(80)),
                   NOW()
            WHERE NOT EXISTS (
              SELECT 1 FROM escritorios WHERE slug = CAST(:slug_check AS VARCHAR(80))
            )
            """
        ),
        {"nome": nome, "slug": slug, "slug_check": slug},
    )
    for table in (
        "users",
        "prazos",
        "processos",
        "convites",
        "feriados",
        "audit_logs",
        "alerta_envios",
    ):
        await conn.execute(
            text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS escritorio_id UUID")
        )
        await conn.execute(
            text(
                f"""
                UPDATE {table}
                SET escritorio_id = (
                    SELECT id FROM escritorios
                    WHERE slug = CAST(:slug AS VARCHAR(80))
                    LIMIT 1
                )
                WHERE escritorio_id IS NULL
                """
            ),
            {"slug": slug},
        )
        await conn.execute(
            text(
                f"""
                DO $$
                BEGIN
                  BEGIN
                    ALTER TABLE {table} ALTER COLUMN escritorio_id SET NOT NULL;
                  EXCEPTION
                    WHEN others THEN NULL;
                  END;
                  BEGIN
                    CREATE INDEX IF NOT EXISTS ix_{table}_escritorio_id
                      ON {table} (escritorio_id);
                  EXCEPTION
                    WHEN others THEN NULL;
                  END;
                  BEGIN
                    ALTER TABLE {table}
                      ADD CONSTRAINT fk_{table}_escritorio
                      FOREIGN KEY (escritorio_id) REFERENCES escritorios(id);
                  EXCEPTION
                    WHEN duplicate_object THEN NULL;
                    WHEN others THEN NULL;
                  END;
                END $$;
                """
            )
        )

    await conn.execute(
        text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_user_escritorio_email
              ON users (escritorio_id, email)
            """
        )
    )
    await conn.execute(
        text(
            "ALTER TABLE processos DROP CONSTRAINT IF EXISTS processos_numero_processo_key"
        )
    )
    await conn.execute(
        text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_processo_escritorio_numero
              ON processos (escritorio_id, numero_processo)
            """
        )
    )
    await conn.execute(
        text("ALTER TABLE feriados DROP CONSTRAINT IF EXISTS feriados_data_key")
    )
    await conn.execute(
        text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_feriado_escritorio_data
              ON feriados (escritorio_id, data)
            """
        )
    )


async def run_processo_backfill() -> None:
    from app.services.processos import backfill_processos

    async with AsyncSessionLocal() as session:
        await backfill_processos(session)
