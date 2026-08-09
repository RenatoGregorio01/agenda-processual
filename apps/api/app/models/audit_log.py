from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class AuditAction(StrEnum):
    login = "login"
    prazo_criado = "prazo_criado"
    prazo_atualizado = "prazo_atualizado"
    prazo_cumprido = "prazo_cumprido"
    prazo_excluido = "prazo_excluido"
    prazo_restaurado = "prazo_restaurado"
    usuario_criado = "usuario_criado"
    usuario_atualizado = "usuario_atualizado"


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    usuario_id: UUID = Field(index=True)
    usuario_nome: str = Field(max_length=120)
    usuario_email: str = Field(max_length=255, index=True)
    acao: AuditAction = Field(index=True)
    entidade: str = Field(default="prazo", max_length=40, index=True)
    entidade_id: UUID | None = Field(default=None, index=True)
    resumo: str = Field(max_length=500)
    criado_em: datetime = Field(default_factory=datetime.utcnow, index=True)
