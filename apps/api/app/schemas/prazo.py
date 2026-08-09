from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.prazo import StatusPrazo


class PrazoCreate(BaseModel):
    numero_processo: str = Field(min_length=1, max_length=64)
    cliente: str = Field(min_length=1, max_length=255)
    acao: str = Field(min_length=1, max_length=255)
    data_disponibilizacao: date | None = None
    data_vencimento: date
    responsavel_id: UUID
    alerta_3_dias: bool = True
    alerta_2_dias: bool = True
    alerta_1_dia: bool = True


class PrazoUpdate(BaseModel):
    numero_processo: str | None = Field(default=None, min_length=1, max_length=64)
    cliente: str | None = Field(default=None, min_length=1, max_length=255)
    acao: str | None = Field(default=None, min_length=1, max_length=255)
    data_disponibilizacao: date | None = None
    data_vencimento: date | None = None
    responsavel_id: UUID | None = None
    status: StatusPrazo | None = None
    alerta_3_dias: bool | None = None
    alerta_2_dias: bool | None = None
    alerta_1_dia: bool | None = None


class PrazoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    numero_processo: str
    cliente: str
    acao: str
    data_disponibilizacao: date | None
    data_vencimento: date
    responsavel: str
    responsavel_id: UUID | None
    status: StatusPrazo
    alerta_3_dias: bool
    alerta_2_dias: bool
    alerta_1_dia: bool
    excluido_em: datetime | None
    criado_em: datetime
    atualizado_em: datetime
