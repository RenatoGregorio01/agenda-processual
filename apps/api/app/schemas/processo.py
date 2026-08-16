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


class DatajudAndamentoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    data_hora: datetime | None = None
    codigo: int | None = None
    nome: str


class DatajudSyncRead(BaseModel):
    status: str
    sincronizado_em: datetime | None = None
    tribunal: str | None = None
    grau: str | None = None
    classe: str | None = None
    orgao: str | None = None
    mensagem: str | None = None
    cache: bool = False
    andamentos: list[DatajudAndamentoRead] = Field(default_factory=list)


class ProcessoValidarRead(BaseModel):
    incompleto: bool = False
    valido: bool | None = None
    mensagem: str | None = None
    mascarado: str | None = None
    cadastrado: bool = False
    processo_id: UUID | None = None
    cliente: str | None = None
    prazos_count: int | None = None
    datajud: str | None = None
    datajud_mensagem: str | None = None


class ProcessoDetail(BaseModel):
    processo: ProcessoRead
    prazos: list[PrazoRead]
    historico: list[AuditLogRead]
    datajud: DatajudSyncRead
