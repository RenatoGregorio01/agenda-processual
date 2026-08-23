from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserRead

__all__ = ["LoginRequest", "TokenResponse", "UserRead"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    escritorio_id: UUID | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginEscritorio(BaseModel):
    id: UUID
    nome: str


class LoginResponse(BaseModel):
    access_token: str | None = None
    token_type: str = "bearer"
    selecionar_escritorio: bool = False
    escritorios: list[LoginEscritorio] = []


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    password: str = Field(min_length=6, max_length=128)
