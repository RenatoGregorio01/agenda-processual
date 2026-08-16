from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class Escritorio(SQLModel, table=True):
    __tablename__ = "escritorios"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nome: str = Field(max_length=120)
    slug: str = Field(index=True, unique=True, max_length=80)
    criado_em: datetime = Field(default_factory=utc_now)
