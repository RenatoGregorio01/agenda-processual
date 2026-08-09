from datetime import date, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Feriado(SQLModel, table=True):
    __tablename__ = "feriados"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    data: date = Field(index=True, unique=True)
    nome: str = Field(max_length=255)
    criado_em: datetime = Field(default_factory=datetime.utcnow)
