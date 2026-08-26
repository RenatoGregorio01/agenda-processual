from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.schemas.auth import TokenResponse
from app.schemas.cadastro import (
    CadastroEnviarCodigoRequest,
    CadastroEnviarCodigoResponse,
    CadastroEscritorioRequest,
)
from app.services.cadastro import cadastrar_escritorio
from app.services.cadastro_codigo import enviar_codigo_cadastro

router = APIRouter()


@router.post("/enviar-codigo", response_model=CadastroEnviarCodigoResponse)
async def enviar_codigo(
    payload: CadastroEnviarCodigoRequest,
    session: AsyncSession = Depends(get_session),
) -> CadastroEnviarCodigoResponse:
    result = await enviar_codigo_cadastro(session, payload.email)
    return CadastroEnviarCodigoResponse(
        ok=True,
        expires_in_seconds=int(result["expires_in_seconds"]),
    )


@router.post("", response_model=TokenResponse)
async def cadastrar(
    payload: CadastroEscritorioRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """Cria escritório + admin após validar o código do e-mail."""
    return await cadastrar_escritorio(session, payload)
