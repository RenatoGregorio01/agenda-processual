from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import Settings
from app.core.security import hash_password
from app.models.user import User


async def seed_admin_user(session: AsyncSession, settings: Settings) -> None:
    if not settings.seed_admin_email or not settings.seed_admin_password:
        return

    email = settings.seed_admin_email.lower()
    result = await session.exec(select(User).where(User.email == email))
    if result.first() is not None:
        return

    user = User(
        email=email,
        nome=settings.seed_admin_name,
        hashed_password=hash_password(settings.seed_admin_password),
        is_admin=True,
        ativo=True,
    )
    session.add(user)
    await session.commit()
