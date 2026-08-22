from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DjenPublicacaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    processo_id: UUID | None = None
    prazo_id: UUID | None = None
    numero_processo: str
    cliente: str | None = None
    tribunal: str | None = None
    tipo_comunicacao: str
    tipo_documento: str | None = None
    nome_classe: str | None = None
    orgao: str | None = None
    texto: str | None = None
    link: str | None = None
    destinatarios: str | None = None
    dias_identificados: int | None = None
    data_disponibilizacao: date | None = None
    vencimento_sugerido: date | None = None
    status: str
    motivo_cancelamento: str | None = None
    sincronizado_em: datetime
    criado_em: datetime


class DjenResumoRead(BaseModel):
    novas: int = 0
    com_prazo: int = 0
    ignoradas: int = 0
    total: int = 0


class DjenSyncRead(BaseModel):
    ok: bool
    cache: bool = False
    criados: int = 0
    mensagem: str | None = None
    publicacoes: list[DjenPublicacaoRead] = Field(default_factory=list)
