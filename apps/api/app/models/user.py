from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class Role(StrEnum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    nome: str = Field(max_length=120)
    hashed_password: str = Field(max_length=255)
    ativo: bool = Field(default=True, index=True)
    role: Role = Field(default=Role.editor, index=True)
    receber_alertas: bool = Field(default=True)
    # Mantido sincronizado com role == admin (compatibilidade)
    is_admin: bool = False
    criado_em: datetime = Field(default_factory=utc_now)
    atualizado_em: datetime = Field(default_factory=utc_now)
