from datetime import date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class StatusPrazo(StrEnum):
    pendente = "pendente"
    cumprido = "cumprido"


class Prazo(SQLModel, table=True):
    __tablename__ = "prazos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    numero_processo: str = Field(index=True, max_length=64)
    cliente: str = Field(max_length=255)
    acao: str = Field(max_length=255)
    data_disponibilizacao: date | None = None
    data_vencimento: date = Field(index=True)
    responsavel: str = Field(max_length=120)
    responsavel_id: UUID | None = Field(default=None, index=True)
    status: StatusPrazo = Field(default=StatusPrazo.pendente, index=True)
    alerta_3_dias: bool = True
    alerta_2_dias: bool = True
    alerta_1_dia: bool = True
    excluido_em: datetime | None = Field(default=None, index=True)
    criado_em: datetime = Field(default_factory=utc_now)
    atualizado_em: datetime = Field(default_factory=utc_now)
