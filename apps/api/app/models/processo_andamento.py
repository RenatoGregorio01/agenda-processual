from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class ProcessoAndamento(SQLModel, table=True):
    __tablename__ = "processo_andamentos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    processo_id: UUID = Field(index=True, foreign_key="processos.id")
    data_hora: datetime | None = Field(default=None, index=True)
    codigo: int | None = Field(default=None)
    nome: str = Field(max_length=255)
    ordem: int = Field(default=0)
    criado_em: datetime = Field(default_factory=utc_now)
