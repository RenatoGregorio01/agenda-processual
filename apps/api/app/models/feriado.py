from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class Feriado(SQLModel, table=True):
    __tablename__ = "feriados"
    __table_args__ = (
        UniqueConstraint("escritorio_id", "data", name="uq_feriado_escritorio_data"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    escritorio_id: UUID = Field(index=True, foreign_key="escritorios.id")
    data: date = Field(index=True)
    nome: str = Field(max_length=255)
    criado_em: datetime = Field(default_factory=utc_now)
