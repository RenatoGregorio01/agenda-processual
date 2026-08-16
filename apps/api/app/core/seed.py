import os
from datetime import date, timedelta

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import Settings
from app.core.permissions import sync_admin_flag
from app.core.security import hash_password
from app.core.timeutils import utc_now
from app.integrations.datajud.cnj import montar_cnj
from app.models.escritorio import Escritorio
from app.models.prazo import Prazo
from app.models.prazo_alerta import DEFAULT_ALERTA_DIAS, PrazoAlerta
from app.models.processo import Processo
from app.models.user import Role, User
from app.services.processos import get_or_create_processo

CNJ_EXEMPLO_LEGADO = {
    "0001234-56.2024.4.01.0000": montar_cnj("0001234", "2024", "4", "01", "0000"),
    "0002222-11.2024.8.26.0100": montar_cnj("0002222", "2024", "8", "26", "0100"),
    "0009876-12.2023.8.05.0001": montar_cnj("0009876", "2023", "8", "05", "0001"),
    "0003333-44.2025.4.01.3400": montar_cnj("0003333", "2025", "4", "01", "3400"),
    "0004444-55.2025.8.26.0001": montar_cnj("0004444", "2025", "8", "26", "0001"),
    "0005555-00.2025.4.01.3300": montar_cnj("0005555", "2025", "4", "01", "3300"),
    "0006666-77.2024.8.26.0100": montar_cnj("0006666", "2024", "8", "26", "0100"),
    "0007777-88.2025.4.01.3300": montar_cnj("0007777", "2025", "4", "01", "3300"),
}


async def seed_escritorio(session: AsyncSession, settings: Settings) -> Escritorio:
    slug = (settings.seed_escritorio_slug or "escritorio").strip().lower()
    result = await session.exec(select(Escritorio).where(Escritorio.slug == slug))
    existing = result.first()
    if existing is not None:
        return existing

    first = (
        await session.exec(select(Escritorio).order_by(Escritorio.criado_em.asc()))
    ).first()
    if first is not None:
        return first

    escritorio = Escritorio(
        nome=settings.seed_escritorio_nome.strip() or "Escritório",
        slug=slug,
    )
    session.add(escritorio)
    await session.commit()
    await session.refresh(escritorio)
    return escritorio


async def seed_admin_user(session: AsyncSession, settings: Settings) -> User | None:
    if not settings.seed_admin_email or not settings.seed_admin_password:
        return None

    escritorio = await seed_escritorio(session, settings)
    email = settings.seed_admin_email.lower()
    result = await session.exec(select(User).where(User.email == email))
    existing = result.first()
    if existing is not None:
        changed = False
        # Se SEED_ADMIN_PASSWORD veio do ambiente, alinha a senha do admin seed
        # (útil no homelab/prod para não ficar com agenda123 após o primeiro boot).
        if os.getenv("SEED_ADMIN_PASSWORD"):
            existing.hashed_password = hash_password(settings.seed_admin_password)
            changed = True
        if existing.role != Role.admin:
            existing.role = Role.admin
            sync_admin_flag(existing)
            changed = True
        if not existing.receber_alertas:
            existing.receber_alertas = True
            changed = True
        if existing.escritorio_id != escritorio.id:
            existing.escritorio_id = escritorio.id
            changed = True
        if changed:
            session.add(existing)
            await session.commit()
        return existing

    user = User(
        escritorio_id=escritorio.id,
        email=email,
        nome=settings.seed_admin_name,
        hashed_password=hash_password(settings.seed_admin_password),
        role=Role.admin,
        ativo=True,
        receber_alertas=True,
    )
    sync_admin_flag(user)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def seed_example_prazos(session: AsyncSession) -> None:
    result = await session.exec(select(Prazo).limit(1))
    if result.first() is not None:
        return

    admin_result = await session.exec(
        select(User).where(User.role == Role.admin).order_by(User.criado_em.asc())
    )
    admin = admin_result.first()
    if admin is None:
        return

    today = date.today()
    maria = montar_cnj("0001234", "2024", "4", "01", "0000")
    exemplos = [
        # Atrasados
        (
            maria,
            "Maria Souza",
            "Protocolar contestação",
            today - timedelta(days=20),
            today - timedelta(days=2),
        ),
        (
            maria,
            "Maria Souza",
            "Apresentar réplica",
            today - timedelta(days=15),
            today - timedelta(days=1),
        ),
        (
            montar_cnj("0002222", "2024", "8", "26", "0100"),
            "Carlos Mendes",
            "Cumprir intimação",
            today - timedelta(days=12),
            today - timedelta(days=5),
        ),
        # Vence hoje
        (
            montar_cnj("0009876", "2023", "8", "05", "0001"),
            "João Lima",
            "Juntar procuração",
            today - timedelta(days=10),
            today,
        ),
        (
            montar_cnj("0003333", "2025", "4", "01", "3400"),
            "Paula Nunes",
            "Protocolar agravo de instrumento",
            today - timedelta(days=8),
            today,
        ),
        (
            montar_cnj("0004444", "2025", "8", "26", "0001"),
            "Ricardo Alves",
            "Apresentar contrarrazões",
            today - timedelta(days=6),
            today,
        ),
        # Vencimentos futuros
        (
            montar_cnj("0005555", "2025", "4", "01", "3300"),
            "Ana Dias",
            "Interpor recurso",
            today - timedelta(days=5),
            today + timedelta(days=1),
        ),
        (
            maria,
            "Maria Souza",
            "Juntar documentos",
            today - timedelta(days=5),
            today + timedelta(days=3),
        ),
        (
            montar_cnj("0006666", "2024", "8", "26", "0100"),
            "Fernanda Costa",
            "Especificar provas",
            today - timedelta(days=4),
            today + timedelta(days=7),
        ),
        (
            montar_cnj("0007777", "2025", "4", "01", "3300"),
            "Bruno Teixeira",
            "Apresentar alegações finais",
            today - timedelta(days=3),
            today + timedelta(days=15),
        ),
    ]

    for numero, cliente, acao, disponibilizacao, vencimento in exemplos:
        processo, _ = await get_or_create_processo(
            session,
            numero_processo=numero,
            cliente=cliente,
            usuario=admin,
        )
        prazo = Prazo(
            escritorio_id=admin.escritorio_id,
            processo_id=processo.id,
            numero_processo=processo.numero_processo,
            cliente=processo.cliente,
            acao=acao,
            data_disponibilizacao=disponibilizacao,
            data_vencimento=vencimento,
            responsavel=admin.nome,
            responsavel_id=admin.id,
        )
        session.add(prazo)
        await session.flush()
        for dias in DEFAULT_ALERTA_DIAS:
            session.add(PrazoAlerta(prazo_id=prazo.id, dias_antes=dias))

    await session.commit()


async def corrigir_cnj_exemplos(session: AsyncSession) -> int:
    """Atualiza números de exemplo antigos (DV inválido) para o CNJ correto."""
    atualizados = 0
    for antigo, novo in CNJ_EXEMPLO_LEGADO.items():
        if antigo == novo:
            continue

        prazos = list(
            (await session.exec(select(Prazo).where(Prazo.numero_processo == antigo))).all()
        )
        processos = list(
            (
                await session.exec(
                    select(Processo).where(Processo.numero_processo == antigo)
                )
            ).all()
        )
        if not prazos and not processos:
            continue

        tenant_id = None
        if processos:
            tenant_id = processos[0].escritorio_id
        elif prazos:
            tenant_id = prazos[0].escritorio_id
        destino_query = select(Processo).where(Processo.numero_processo == novo)
        if tenant_id is not None:
            destino_query = destino_query.where(Processo.escritorio_id == tenant_id)
        destino = (await session.exec(destino_query)).first()

        for processo in processos:
            if destino is not None and destino.id != processo.id:
                for prazo in prazos:
                    if prazo.processo_id == processo.id:
                        prazo.processo_id = destino.id
                        session.add(prazo)
                await session.delete(processo)
            else:
                processo.numero_processo = novo
                processo.atualizado_em = utc_now()
                session.add(processo)
                destino = processo

        for prazo in prazos:
            prazo.numero_processo = novo
            if destino is not None:
                prazo.processo_id = destino.id
            session.add(prazo)
            atualizados += 1

    if atualizados:
        await session.commit()
    return atualizados
