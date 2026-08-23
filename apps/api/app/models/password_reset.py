from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class PasswordReset(SQLModel, table=True):
    __tablename__ = "password_resets"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    account_id: UUID = Field(index=True, foreign_key="contas.id")
    token_hash: str = Field(index=True, unique=True, max_length=64)
    expires_at: datetime = Field(index=True)
    used_at: datetime | None = Field(default=None, index=True)
    criado_em: datetime = Field(default_factory=utc_now)
