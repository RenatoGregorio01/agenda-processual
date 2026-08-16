from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.permissions import Permission
from app.models.user import Role


class UserCreate(BaseModel):
    email: EmailStr
    nome: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=6, max_length=128)
    role: Role = Role.editor
    ativo: bool = True
    receber_alertas: bool = False


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    password: str | None = Field(default=None, min_length=6, max_length=128)
    role: Role | None = None
    ativo: bool | None = None
    receber_alertas: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    escritorio_id: UUID
    escritorio_nome: str = ""
    email: EmailStr
    nome: str
    ativo: bool
    role: Role
    receber_alertas: bool
    is_admin: bool
    permissions: list[Permission] = []


class UserOption(BaseModel):
    id: UUID
    nome: str


class RoleInfo(BaseModel):
    id: Role
    label: str
    description: str
    permissions: list[Permission]
    permission_labels: list[str]
