from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import Role


class ConviteCreate(BaseModel):
    email: EmailStr
    nome: str = Field(min_length=1, max_length=120)
    role: Role = Role.editor
    receber_alertas: bool = False


class ConviteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    nome: str
    role: Role
    receber_alertas: bool
    expires_at: datetime
    used_at: datetime | None
    revoked_at: datetime | None
    invited_by_id: UUID
    criado_em: datetime
    status: str


class ConvitePublic(BaseModel):
    email: EmailStr
    nome: str
    role: Role
    expires_at: datetime


class ConviteAccept(BaseModel):
    password: str = Field(min_length=6, max_length=128)
