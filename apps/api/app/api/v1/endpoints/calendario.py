from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_permission
from app.core.database import get_session
from app.core.permissions import Permission
from app.models.feriado import Feriado
from app.schemas.calendario import CalcularVencimentoRequest, CalcularVencimentoResponse
from app.services.dias_uteis import add_business_days

router = APIRouter()


@router.post(
    "/calcular-vencimento",
    response_model=CalcularVencimentoResponse,
    dependencies=[Depends(require_permission(Permission.prazos_criar))],
)
async def calcular_vencimento(
    payload: CalcularVencimentoRequest,
    session: AsyncSession = Depends(get_session),
) -> CalcularVencimentoResponse:
    result = await session.exec(select(Feriado))
    feriados = {item.data for item in result.all()}
    vencimento = add_business_days(payload.data_base, payload.dias, feriados)

    inicio = payload.data_base + timedelta(days=1)
    feriados_intervalo = sorted(
        day for day in feriados if inicio <= day <= vencimento
    )

    return CalcularVencimentoResponse(
        data_base=payload.data_base,
        dias=payload.dias,
        data_vencimento=vencimento,
        feriados_no_intervalo=feriados_intervalo,
    )
