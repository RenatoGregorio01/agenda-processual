from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now

ALERTA_DIAS_MIN = 1
ALERTA_DIAS_MAX = 365
DEFAULT_ALERTA_DIAS = [3, 1]


class PrazoAlerta(SQLModel, table=True):
    __tablename__ = "prazo_alertas"
    __table_args__ = (
        UniqueConstraint("prazo_id", "dias_antes", name="uq_prazo_alerta_prazo_dias"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    prazo_id: UUID = Field(index=True, foreign_key="prazos.id")
    dias_antes: int = Field(index=True)
    criado_em: datetime = Field(default_factory=utc_now)
