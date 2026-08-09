from datetime import date, timedelta

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import Settings
from app.core.permissions import sync_admin_flag
from app.core.security import hash_password
from app.models.prazo import Prazo
from app.models.user import Role, User


async def seed_admin_user(session: AsyncSession, settings: Settings) -> None:
    if not settings.seed_admin_email or not settings.seed_admin_password:
        return

    email = settings.seed_admin_email.lower()
    result = await session.exec(select(User).where(User.email == email))
    existing = result.first()
    if existing is not None:
        if existing.role != Role.admin:
            existing.role = Role.admin
            sync_admin_flag(existing)
            session.add(existing)
            await session.commit()
        return

    user = User(
        email=email,
        nome=settings.seed_admin_name,
        hashed_password=hash_password(settings.seed_admin_password),
        role=Role.admin,
        ativo=True,
    )
    sync_admin_flag(user)
    session.add(user)
    await session.commit()


async def seed_example_prazos(session: AsyncSession) -> None:
    result = await session.exec(select(Prazo).limit(1))
    if result.first() is not None:
        return

    today = date.today()
    exemplos = [
        Prazo(
            numero_processo="0001234-56.2024.4.01.0000",
            cliente="Maria Souza",
            acao="Protocolar contestação",
            data_disponibilizacao=today - timedelta(days=20),
            data_vencimento=today - timedelta(days=1),
            responsavel="Verônica",
        ),
        Prazo(
            numero_processo="0009876-12.2023.8.05.0001",
            cliente="João Lima",
            acao="Juntar procuração",
            data_disponibilizacao=today - timedelta(days=10),
            data_vencimento=today + timedelta(days=1),
            responsavel="Verônica",
        ),
        Prazo(
            numero_processo="0005555-00.2025.4.01.3300",
            cliente="Ana Dias",
            acao="Interpor recurso",
            data_disponibilizacao=today - timedelta(days=5),
            data_vencimento=today + timedelta(days=3),
            responsavel="Estagiário",
        ),
    ]
    session.add_all(exemplos)
    await session.commit()
