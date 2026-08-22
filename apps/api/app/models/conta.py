from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class Conta(SQLModel, table=True):
    """Identidade global; o acesso a cada escritório fica em User."""

    __tablename__ = "contas"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    nome: str = Field(max_length=120)
    hashed_password: str = Field(max_length=255)
    ativo: bool = Field(default=True, index=True)
    criado_em: datetime = Field(default_factory=utc_now)
    atualizado_em: datetime = Field(default_factory=utc_now)
