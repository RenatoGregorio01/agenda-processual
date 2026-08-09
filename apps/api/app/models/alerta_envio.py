from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class TipoAlerta(StrEnum):
    dias_3 = "3dias"
    dias_2 = "2dias"
    dias_1 = "1dia"


class AlertaEnvio(SQLModel, table=True):
    __tablename__ = "alerta_envios"
    __table_args__ = (
        UniqueConstraint(
            "prazo_id",
            "tipo",
            "destinatario_email",
            name="uq_alerta_envio_prazo_tipo_email",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    prazo_id: UUID = Field(index=True)
    tipo: TipoAlerta = Field(index=True, max_length=20)
    destinatario_email: str = Field(max_length=255, index=True)
    enviado_em: datetime = Field(default_factory=datetime.utcnow)
