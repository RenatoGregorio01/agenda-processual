from datetime import date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Column, Text, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class DjenStatus(StrEnum):
    nova = "nova"
    prazo_criado = "prazo_criado"
    ignorada = "ignorada"


class DjenPublicacao(SQLModel, table=True):
    __tablename__ = "djen_publicacoes"
    __table_args__ = (
        UniqueConstraint(
            "escritorio_id",
            "djen_id",
            name="uq_djen_escritorio_id",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    escritorio_id: UUID = Field(index=True, foreign_key="escritorios.id")
    processo_id: UUID | None = Field(default=None, index=True, foreign_key="processos.id")
    prazo_id: UUID | None = Field(default=None, index=True, foreign_key="prazos.id")
    djen_id: str = Field(index=True, max_length=40)
    hash: str | None = Field(default=None, max_length=80)
    numero_processo: str = Field(index=True, max_length=64)
    numero_processo_digitos: str = Field(index=True, max_length=20)
    tribunal: str | None = Field(default=None, max_length=20)
    tipo_comunicacao: str = Field(max_length=80)
    tipo_documento: str | None = Field(default=None, max_length=80)
    nome_classe: str | None = Field(default=None, max_length=255)
    orgao: str | None = Field(default=None, max_length=255)
    texto: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    link: str | None = Field(default=None, max_length=500)
    destinatarios: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    dias_identificados: int | None = Field(default=None)
    data_disponibilizacao: date | None = Field(default=None, index=True)
    status: DjenStatus = Field(default=DjenStatus.nova, index=True)
    motivo_cancelamento: str | None = Field(default=None, max_length=500)
    sincronizado_em: datetime = Field(default_factory=utc_now)
    criado_em: datetime = Field(default_factory=utc_now)
    atualizado_em: datetime = Field(default_factory=utc_now)
