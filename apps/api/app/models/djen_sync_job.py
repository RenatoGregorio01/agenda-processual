from datetime import date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class DjenSyncJobStatus(StrEnum):
    pendente = "pendente"
    processando = "processando"
    concluido = "concluido"
    erro = "erro"


class DjenSyncJob(SQLModel, table=True):
    __tablename__ = "djen_sync_jobs"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    escritorio_id: UUID = Field(index=True, foreign_key="escritorios.id")
    usuario_id: UUID | None = Field(default=None, index=True, foreign_key="users.id")
    numero_oab: str = Field(max_length=20, index=True)
    uf_oab: str = Field(max_length=2, index=True)
    data_inicio: date = Field(index=True)
    data_fim: date = Field(index=True)
    status: DjenSyncJobStatus = Field(default=DjenSyncJobStatus.pendente, index=True)
    publicacoes_criadas: int = Field(default=0)
    mensagem_erro: str | None = Field(default=None, max_length=500)
    criado_em: datetime = Field(default_factory=utc_now)
    iniciado_em: datetime | None = Field(default=None)
    concluido_em: datetime | None = Field(default=None)
