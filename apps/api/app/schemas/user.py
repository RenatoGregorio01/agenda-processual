from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    nome: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=6, max_length=128)
    is_admin: bool = False
    ativo: bool = True


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    password: str | None = Field(default=None, min_length=6, max_length=128)
    is_admin: bool | None = None
    ativo: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    nome: str
    ativo: bool
    is_admin: bool
