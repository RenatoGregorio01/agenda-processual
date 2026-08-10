from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.audit import AuditLogRead
from app.schemas.prazo import PrazoRead


class ProcessoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    numero_processo: str
    cliente: str
    criado_em: datetime
    atualizado_em: datetime
    prazos_count: int = 0


class ProcessoUpdate(BaseModel):
    cliente: str | None = Field(default=None, min_length=1, max_length=255)


class ProcessoDetail(BaseModel):
    processo: ProcessoRead
    prazos: list[PrazoRead]
    historico: list[AuditLogRead]
