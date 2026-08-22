from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.schemas.auth import TokenResponse
from app.schemas.cadastro import CadastroEscritorioRequest
from app.services.cadastro import cadastrar_escritorio

router = APIRouter()


@router.post("", response_model=TokenResponse)
async def cadastrar(
    payload: CadastroEscritorioRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """Cria escritório + admin e retorna token (login imediato)."""
    return await cadastrar_escritorio(session, payload)
