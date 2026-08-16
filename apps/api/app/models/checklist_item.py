from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.core.timeutils import utc_now


class ChecklistItem(SQLModel, table=True):
    __tablename__ = "checklist_itens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    prazo_id: UUID = Field(index=True, foreign_key="prazos.id")
    texto: str = Field(max_length=255)
    concluido: bool = Field(default=False, index=True)
    ordem: int = Field(default=0)
    criado_em: datetime = Field(default_factory=utc_now)
    atualizado_em: datetime = Field(default_factory=utc_now)
