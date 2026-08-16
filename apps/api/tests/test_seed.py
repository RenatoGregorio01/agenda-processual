from datetime import date

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.seed import CNJ_EXEMPLO_LEGADO, corrigir_cnj_exemplos
from app.models.escritorio import Escritorio
from app.models.prazo import Prazo
from app.models.processo import Processo


@pytest.mark.asyncio
async def test_corrigir_cnj_exemplos_atualiza_numeros_legados() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    antigo = "0001234-56.2024.4.01.0000"
    novo = CNJ_EXEMPLO_LEGADO[antigo]
    async with session_factory() as session:
        escritorio = Escritorio(nome="Escritório", slug="escritorio")
        session.add(escritorio)
        await session.flush()
        processo = Processo(
            escritorio_id=escritorio.id,
            numero_processo=antigo,
            cliente="Maria Souza",
        )
        session.add(processo)
        await session.flush()
        session.add(
            Prazo(
                escritorio_id=escritorio.id,
                processo_id=processo.id,
                numero_processo=antigo,
                cliente="Maria Souza",
                acao="Protocolar contestação",
                data_vencimento=date.today(),
                responsavel="Verônica",
            )
        )
        await session.commit()

        atualizados = await corrigir_cnj_exemplos(session)
        assert atualizados == 1

        prazo = (await session.exec(select(Prazo))).first()
        processo = (await session.exec(select(Processo))).first()
        assert prazo is not None
        assert processo is not None
        assert prazo.numero_processo == novo
        assert processo.numero_processo == novo

    await engine.dispose()
