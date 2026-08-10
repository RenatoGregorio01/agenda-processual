from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class Processo(SQLModel, table=True):
    __tablename__ = "processos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    numero_processo: str = Field(index=True, unique=True, max_length=64)
    cliente: str = Field(max_length=255)
    criado_em: datetime = Field(default_factory=utc_now)
    atualizado_em: datetime = Field(default_factory=utc_now)
