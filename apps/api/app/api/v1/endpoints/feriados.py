from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_admin, require_permission
from app.core.database import get_session
from app.core.permissions import Permission
from app.models.audit_log import AuditAction
from app.models.feriado import Feriado
from app.models.user import User
from app.schemas.feriado import FeriadoCreate, FeriadoRead, FeriadoUpdate
from app.services.audit import montar_auditoria

router = APIRouter()


@router.get(
    "",
    response_model=list[FeriadoRead],
    dependencies=[Depends(require_permission(Permission.prazos_visualizar))],
)
async def listar_feriados(
    session: AsyncSession = Depends(get_session),
) -> list[Feriado]:
    result = await session.exec(select(Feriado).order_by(col(Feriado.data).asc()))
    return list(result.all())


@router.post(
    "",
    response_model=FeriadoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
async def criar_feriado(
    payload: FeriadoCreate,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
) -> Feriado:
    existing = await session.exec(select(Feriado).where(Feriado.data == payload.data))
    if existing.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe feriado nesta data",
        )

    feriado = Feriado(data=payload.data, nome=payload.nome.strip())
    session.add(feriado)
    await session.flush()
    session.add(
        montar_auditoria(
            usuario=current_admin,
            acao=AuditAction.feriado_criado,
            entidade="feriado",
            entidade_id=feriado.id,
            resumo=f"Cadastrou feriado {feriado.nome} em {feriado.data.isoformat()}",
        )
    )
    await session.commit()
    await session.refresh(feriado)
    return feriado


@router.patch(
    "/{feriado_id}",
    response_model=FeriadoRead,
    dependencies=[Depends(get_current_admin)],
)
async def atualizar_feriado(
    feriado_id: UUID,
    payload: FeriadoUpdate,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
) -> Feriado:
    feriado = await session.get(Feriado, feriado_id)
    if feriado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feriado não encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "nome" in data and data["nome"] is not None:
        data["nome"] = data["nome"].strip()
    if "data" in data and data["data"] is not None and data["data"] != feriado.data:
        existing = await session.exec(select(Feriado).where(Feriado.data == data["data"]))
        if existing.first() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe feriado nesta data",
            )

    for key, value in data.items():
        setattr(feriado, key, value)

    session.add(feriado)
    session.add(
        montar_auditoria(
            usuario=current_admin,
            acao=AuditAction.feriado_atualizado,
            entidade="feriado",
            entidade_id=feriado.id,
            resumo=f"Atualizou feriado {feriado.nome} ({feriado.data.isoformat()})",
        )
    )
    await session.commit()
    await session.refresh(feriado)
    return feriado


@router.delete(
    "/{feriado_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
async def excluir_feriado(
    feriado_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
) -> None:
    feriado = await session.get(Feriado, feriado_id)
    if feriado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feriado não encontrado")

    session.add(
        montar_auditoria(
            usuario=current_admin,
            acao=AuditAction.feriado_excluido,
            entidade="feriado",
            entidade_id=feriado.id,
            resumo=f"Excluiu feriado {feriado.nome} em {feriado.data.isoformat()}",
        )
    )
    await session.delete(feriado)
    await session.commit()
