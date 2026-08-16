from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class Processo(SQLModel, table=True):
    __tablename__ = "processos"
    __table_args__ = (
        UniqueConstraint(
            "escritorio_id",
            "numero_processo",
            name="uq_processo_escritorio_numero",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    escritorio_id: UUID = Field(index=True, foreign_key="escritorios.id")
    numero_processo: str = Field(index=True, max_length=64)
    cliente: str = Field(max_length=255)
    criado_em: datetime = Field(default_factory=utc_now)
    atualizado_em: datetime = Field(default_factory=utc_now)
    datajud_status: str | None = Field(default=None, max_length=40)
    datajud_sincronizado_em: datetime | None = Field(default=None)
    datajud_tribunal: str | None = Field(default=None, max_length=20)
    datajud_grau: str | None = Field(default=None, max_length=20)
    datajud_classe: str | None = Field(default=None, max_length=255)
    datajud_orgao: str | None = Field(default=None, max_length=255)
    datajud_mensagem: str | None = Field(default=None, max_length=500)
