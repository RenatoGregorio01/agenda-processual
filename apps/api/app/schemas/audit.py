from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.audit_log import AuditAction


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    usuario_nome: str
    usuario_email: EmailStr
    acao: AuditAction
    entidade: str
    entidade_id: UUID | None
    resumo: str
    criado_em: datetime


class PurgeAuditoriaResponse(BaseModel):
    apagados: int
    retention_days: int
