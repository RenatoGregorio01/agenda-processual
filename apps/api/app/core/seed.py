from datetime import date, timedelta

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import Settings
from app.core.permissions import sync_admin_flag
from app.core.security import hash_password
from app.models.prazo import Prazo
from app.models.user import Role, User


async def seed_admin_user(session: AsyncSession, settings: Settings) -> User | None:
    if not settings.seed_admin_email or not settings.seed_admin_password:
        return None

    email = settings.seed_admin_email.lower()
    result = await session.exec(select(User).where(User.email == email))
    existing = result.first()
    if existing is not None:
        changed = False
        if existing.role != Role.admin:
            existing.role = Role.admin
            sync_admin_flag(existing)
            changed = True
        if not existing.receber_alertas:
            existing.receber_alertas = True
            changed = True
        if changed:
            session.add(existing)
            await session.commit()
        return existing

    user = User(
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
    exemplos = [
        Prazo(
            numero_processo="0001234-56.2024.4.01.0000",
            cliente="Maria Souza",
            acao="Protocolar contestação",
            data_disponibilizacao=today - timedelta(days=20),
            data_vencimento=today - timedelta(days=1),
            responsavel=admin.nome,
            responsavel_id=admin.id,
        ),
        Prazo(
            numero_processo="0009876-12.2023.8.05.0001",
            cliente="João Lima",
            acao="Juntar procuração",
            data_disponibilizacao=today - timedelta(days=10),
            data_vencimento=today + timedelta(days=1),
            responsavel=admin.nome,
            responsavel_id=admin.id,
        ),
        Prazo(
            numero_processo="0005555-00.2025.4.01.3300",
            cliente="Ana Dias",
            acao="Interpor recurso",
            data_disponibilizacao=today - timedelta(days=5),
            data_vencimento=today + timedelta(days=3),
            responsavel=admin.nome,
            responsavel_id=admin.id,
        ),
    ]
    session.add_all(exemplos)
    await session.commit()
