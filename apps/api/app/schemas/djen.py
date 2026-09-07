from datetime import date, datetime
from typing import Any
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
    classificacao_ato: str = "outro"
    confianca_prazo: str = "nenhuma"
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


class DjenHistoricoRequest(BaseModel):
    data_inicio: date


class DjenSyncJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    numero_oab: str
    uf_oab: str
    data_inicio: date
    data_fim: date
    status: str
    publicacoes_criadas: int
    mensagem_erro: str | None = None
    criado_em: datetime
    iniciado_em: datetime | None = None
    concluido_em: datetime | None = None


class DjenSyncJobComplete(BaseModel):
    items: list[dict[str, Any]] = Field(default_factory=list)


class DjenSyncJobFail(BaseModel):
    mensagem: str = Field(min_length=1, max_length=500)
