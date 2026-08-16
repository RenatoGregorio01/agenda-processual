from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChecklistItemCreate(BaseModel):
    texto: str = Field(min_length=1, max_length=255)


class ChecklistItemUpdate(BaseModel):
    texto: str | None = Field(default=None, min_length=1, max_length=255)
    concluido: bool | None = None


class ChecklistItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    prazo_id: UUID
    texto: str
    concluido: bool
    ordem: int
    criado_em: datetime
    atualizado_em: datetime
