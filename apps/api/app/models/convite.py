from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.user import Role


class Convite(SQLModel, table=True):
    __tablename__ = "convites"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, max_length=255)
    nome: str = Field(max_length=120)
    role: Role = Field(default=Role.editor, index=True)
    receber_alertas: bool = Field(default=True)
    token_hash: str = Field(index=True, unique=True, max_length=64)
    expires_at: datetime = Field(index=True)
    used_at: datetime | None = Field(default=None, index=True)
    revoked_at: datetime | None = Field(default=None)
    invited_by_id: UUID = Field(index=True)
    criado_em: datetime = Field(default_factory=datetime.utcnow)
