from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FeriadoCreate(BaseModel):
    data: date
    nome: str = Field(min_length=1, max_length=255)


class FeriadoUpdate(BaseModel):
    data: date | None = None
    nome: str | None = Field(default=None, min_length=1, max_length=255)


class FeriadoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    data: date
    nome: str
    criado_em: datetime
