from datetime import date

from pydantic import BaseModel, Field


class CalcularVencimentoRequest(BaseModel):
    data_base: date
    dias: int = Field(ge=1, le=3650)


class FeriadoNoIntervalo(BaseModel):
    data: date
    nome: str


class CalcularVencimentoResponse(BaseModel):
    data_base: date
    dias: int
    data_vencimento: date
    feriados_no_intervalo: list[FeriadoNoIntervalo]

