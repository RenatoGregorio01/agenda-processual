from pydantic import BaseModel, EmailStr, Field


class CadastroEnviarCodigoRequest(BaseModel):
    email: EmailStr


class CadastroEnviarCodigoResponse(BaseModel):
    ok: bool = True
    expires_in_seconds: int


class CadastroEscritorioRequest(BaseModel):
    escritorio_nome: str = Field(min_length=1, max_length=120)
    slug: str | None = Field(default=None, max_length=80)
    nome: str = Field(min_length=1, max_length=120)
    email: EmailStr
    codigo: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=6, max_length=128)
    eh_advogado: bool = False
    oab_numero: str | None = Field(default=None, max_length=20)
    oab_uf: str | None = Field(default=None, max_length=2)
