from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class AlertaEnvio(SQLModel, table=True):
    __tablename__ = "alerta_envios"
    __table_args__ = (
        UniqueConstraint(
            "prazo_id",
            "dias_antes",
            "destinatario_email",
            name="uq_alerta_envio_prazo_dias_email",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    escritorio_id: UUID = Field(index=True, foreign_key="escritorios.id")
    prazo_id: UUID = Field(index=True)
    dias_antes: int = Field(index=True)
    destinatario_email: str = Field(max_length=255, index=True)
    enviado_em: datetime = Field(default_factory=utc_now)
