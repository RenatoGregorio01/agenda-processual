from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.integrations.datajud.cnj import CnjError, validar_cnj
from app.models.prazo import StatusPrazo
from app.models.prazo_alerta import ALERTA_DIAS_MAX, ALERTA_DIAS_MIN, DEFAULT_ALERTA_DIAS


def _normalize_alertas(values: list[int]) -> list[int]:
    unique: list[int] = []
    seen: set[int] = set()
    for value in values:
        if value in seen:
            continue
        if value < ALERTA_DIAS_MIN or value > ALERTA_DIAS_MAX:
            raise ValueError(
                f"Informe entre {ALERTA_DIAS_MIN} e {ALERTA_DIAS_MAX} dias de antecedência"
            )
        seen.add(value)
        unique.append(value)
    unique.sort(reverse=True)
    return unique


def _validar_numero_processo(value: str) -> str:
    try:
        return validar_cnj(value)
    except CnjError as exc:
        raise ValueError(str(exc)) from exc


class PrazoAlertaRead(BaseModel):
    dias_antes: int
    enviado: bool = False


class PrazoCreate(BaseModel):
    numero_processo: str = Field(min_length=1, max_length=64)
    cliente: str = Field(min_length=1, max_length=255)
    acao: str = Field(min_length=1, max_length=255)
    data_disponibilizacao: date | None = None
    data_vencimento: date
    responsavel_id: UUID
    alertas: list[int] = Field(default_factory=lambda: list(DEFAULT_ALERTA_DIAS))

    @field_validator("alertas")
    @classmethod
    def validate_alertas(cls, value: list[int]) -> list[int]:
        return _normalize_alertas(value)

    @field_validator("numero_processo")
    @classmethod
    def validate_numero_processo(cls, value: str) -> str:
        return _validar_numero_processo(value)


class PrazoUpdate(BaseModel):
    numero_processo: str | None = Field(default=None, min_length=1, max_length=64)
    cliente: str | None = Field(default=None, min_length=1, max_length=255)
    acao: str | None = Field(default=None, min_length=1, max_length=255)
    data_disponibilizacao: date | None = None
    data_vencimento: date | None = None
    responsavel_id: UUID | None = None
    status: StatusPrazo | None = None
    alertas: list[int] | None = None

    @field_validator("alertas")
    @classmethod
    def validate_alertas(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return None
        return _normalize_alertas(value)

    @field_validator("numero_processo")
    @classmethod
    def validate_numero_processo(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _validar_numero_processo(value)


class PrazoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    processo_id: UUID | None = None
    numero_processo: str
    cliente: str
    acao: str
    data_disponibilizacao: date | None
    data_vencimento: date
    responsavel: str
    responsavel_id: UUID | None
    status: StatusPrazo
    alertas: list[PrazoAlertaRead] = Field(default_factory=list)
    excluido_em: datetime | None
    criado_em: datetime
    atualizado_em: datetime
