from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_admin
from app.core.config import get_settings
from app.core.database import get_session
from app.models.user import User
from app.schemas.alerta import ProcessarAlertasResponse
from app.services.alertas import processar_alertas

router = APIRouter()


@router.post("/processar", response_model=ProcessarAlertasResponse)
async def disparar_processamento_alertas(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
) -> ProcessarAlertasResponse:
    result = await processar_alertas(session, settings=get_settings())
    return ProcessarAlertasResponse(
        candidatos=result.candidatos,
        enviados=result.enviados,
        ignorados=result.ignorados,
        erros=result.erros,
    )
