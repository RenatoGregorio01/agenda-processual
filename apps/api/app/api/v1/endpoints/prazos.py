from datetime import date
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_permission
from app.core.database import get_session
from app.core.permissions import Permission
from app.core.tenant import get_owned
from app.core.timeutils import utc_now
from app.models.audit_log import AuditAction
from app.models.djen_publicacao import DjenPublicacao, DjenStatus
from app.models.prazo import Prazo, StatusPrazo
from app.models.user import User
from app.schemas.prazo import PrazoCreate, PrazoRead, PrazoUpdate
from app.services.alertas import replace_alertas, to_prazo_read, to_prazos_read
from app.services.audit import montar_auditoria
from app.services.djen import vincular_ao_prazo
from app.services.export_pauta import build_csv, build_pdf, describe_export
from app.services.prazos_query import FiltroPrazo, listar_prazos_filtrados
from app.services.processos import get_or_create_processo

router = APIRouter()

ExportFormat = Literal["csv", "pdf"]


async def _get_prazo_ativo(
    session: AsyncSession, prazo_id: UUID, tenant_id: UUID
) -> Prazo:
    prazo = await get_owned(
        session, Prazo, prazo_id, tenant_id, detail="Prazo não encontrado"
    )
    if prazo.excluido_em is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prazo não encontrado")
    return prazo


async def _resolve_responsavel(
    session: AsyncSession, responsavel_id: UUID, tenant_id: UUID
) -> User:
    user = await session.get(User, responsavel_id)
    if user is None or not user.ativo or user.escritorio_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Responsável inválido ou inativo",
        )
    return user


@router.get(
    "",
    response_model=list[PrazoRead],
)
async def listar_prazos(
    filtro: FiltroPrazo = Query(default="todos"),
    responsavel_id: UUID | None = Query(default=None),
    q: str | None = Query(default=None, max_length=120),
    data_inicio: date | None = Query(default=None),
    data_fim: date | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> list[PrazoRead]:
    if data_inicio and data_fim and data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data inicial não pode ser maior que a data final",
        )

    using_range = data_inicio is not None or data_fim is not None
    prazos = await listar_prazos_filtrados(
        session,
        escritorio_id=current_user.escritorio_id,
        filtro=filtro if not using_range else "todos",
        responsavel_id=responsavel_id,
        q=q,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    return await to_prazos_read(session, prazos)


@router.get("/export")
async def exportar_prazos(
    formato: ExportFormat = Query(default="csv"),
    filtro: FiltroPrazo = Query(default="7dias"),
    data_inicio: date | None = Query(default=None),
    data_fim: date | None = Query(default=None),
    responsavel_id: UUID | None = Query(default=None),
    q: str | None = Query(default=None, max_length=120),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> Response:
    if data_inicio and data_fim and data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data inicial não pode ser maior que a data final",
        )

    using_range = data_inicio is not None or data_fim is not None
    prazos = await listar_prazos_filtrados(
        session,
        escritorio_id=current_user.escritorio_id,
        filtro=filtro if not using_range else "todos",
        responsavel_id=responsavel_id,
        q=q,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    titulo, filename_base = describe_export(
        filtro=None if using_range else filtro,
        data_inicio=data_inicio if using_range else None,
        data_fim=data_fim if using_range else None,
    )

    if formato == "pdf":
        content = build_pdf(prazos, titulo=titulo)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename_base}.pdf"'
            },
        )

    content = build_csv(prazos)
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename_base}.csv"'
        },
    )


@router.post(
    "",
    response_model=PrazoRead,
    status_code=status.HTTP_201_CREATED,
)
async def criar_prazo(
    payload: PrazoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_criar)),
) -> PrazoRead:
    responsavel = await _resolve_responsavel(
        session, payload.responsavel_id, current_user.escritorio_id
    )
    processo, _ = await get_or_create_processo(
        session,
        numero_processo=payload.numero_processo,
        cliente=payload.cliente,
        usuario=current_user,
    )
    data = payload.model_dump()
    data.pop("numero_processo", None)
    data.pop("cliente", None)
    alertas = data.pop("alertas")
    djen_publicacao_id = data.pop("djen_publicacao_id", None)
    publicacao = None
    if djen_publicacao_id is not None:
        publicacao = await get_owned(
            session,
            DjenPublicacao,
            djen_publicacao_id,
            current_user.escritorio_id,
            detail="Publicação DJEN não encontrada",
        )
        if publicacao.status == DjenStatus.prazo_criado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta publicação já gerou um prazo.",
            )
        if publicacao.motivo_cancelamento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta publicação foi cancelada no DJEN.",
            )
    prazo = Prazo(
        **data,
        escritorio_id=current_user.escritorio_id,
        processo_id=processo.id,
        numero_processo=processo.numero_processo,
        cliente=processo.cliente,
        responsavel=responsavel.nome,
    )
    session.add(prazo)
    await session.flush()
    await replace_alertas(session, prazo.id, alertas)
    if publicacao is not None:
        await vincular_ao_prazo(session, publicacao, prazo.id)
    processo.atualizado_em = utc_now()
    session.add(processo)
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.prazo_criado,
            entidade_id=prazo.id,
            resumo=f"Criou prazo: {prazo.acao} ({prazo.numero_processo})",
        )
    )
    await session.commit()
    await session.refresh(prazo)
    return await to_prazo_read(session, prazo)


@router.get(
    "/{prazo_id}",
    response_model=PrazoRead,
)
async def obter_prazo(
    prazo_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> PrazoRead:
    prazo = await get_owned(
        session, Prazo, prazo_id, current_user.escritorio_id, detail="Prazo não encontrado"
    )
    return await to_prazo_read(session, prazo)


@router.patch("/{prazo_id}", response_model=PrazoRead)
async def atualizar_prazo(
    prazo_id: UUID,
    payload: PrazoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_alterar)),
) -> PrazoRead:
    prazo = await _get_prazo_ativo(session, prazo_id, current_user.escritorio_id)
    data = payload.model_dump(exclude_unset=True)

    if "responsavel_id" in data and data["responsavel_id"] is not None:
        responsavel = await _resolve_responsavel(
            session, data["responsavel_id"], current_user.escritorio_id
        )
        prazo.responsavel_id = responsavel.id
        prazo.responsavel = responsavel.nome
        data.pop("responsavel_id")

    numero = data.pop("numero_processo", None)
    cliente = data.pop("cliente", None)
    alertas = data.pop("alertas", None)
    if numero is not None or cliente is not None:
        processo, _ = await get_or_create_processo(
            session,
            numero_processo=numero if numero is not None else prazo.numero_processo,
            cliente=cliente if cliente is not None else prazo.cliente,
            usuario=current_user,
        )
        prazo.processo_id = processo.id
        prazo.numero_processo = processo.numero_processo
        prazo.cliente = processo.cliente
        processo.atualizado_em = utc_now()
        session.add(processo)

    for field, value in data.items():
        setattr(prazo, field, value)
    if alertas is not None:
        await replace_alertas(session, prazo.id, alertas)
    prazo.atualizado_em = utc_now()

    session.add(prazo)
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.prazo_atualizado,
            entidade_id=prazo.id,
            resumo=f"Editou prazo: {prazo.acao} ({prazo.numero_processo})",
        )
    )
    await session.commit()
    await session.refresh(prazo)
    return await to_prazo_read(session, prazo)


@router.post("/{prazo_id}/cumprir", response_model=PrazoRead)
async def marcar_cumprido(
    prazo_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_cumprir)),
) -> PrazoRead:
    prazo = await _get_prazo_ativo(session, prazo_id, current_user.escritorio_id)
    prazo.status = StatusPrazo.cumprido
    prazo.atualizado_em = utc_now()
    session.add(prazo)
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.prazo_cumprido,
            entidade_id=prazo.id,
            resumo=f"Marcou como cumprido: {prazo.acao} ({prazo.numero_processo})",
        )
    )
    await session.commit()
    await session.refresh(prazo)
    return await to_prazo_read(session, prazo)


@router.post("/{prazo_id}/restaurar", response_model=PrazoRead)
async def restaurar_prazo(
    prazo_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_restaurar)),
) -> PrazoRead:
    prazo = await get_owned(
        session, Prazo, prazo_id, current_user.escritorio_id, detail="Prazo excluído não encontrado"
    )
    if prazo.excluido_em is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prazo excluído não encontrado",
        )

    prazo.excluido_em = None
    prazo.atualizado_em = utc_now()
    session.add(prazo)
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.prazo_restaurado,
            entidade_id=prazo.id,
            resumo=f"Restaurou prazo: {prazo.acao} ({prazo.numero_processo})",
        )
    )
    await session.commit()
    await session.refresh(prazo)
    return await to_prazo_read(session, prazo)


@router.delete("/{prazo_id}", response_model=PrazoRead)
async def excluir_prazo(
    prazo_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_excluir)),
) -> PrazoRead:
    prazo = await _get_prazo_ativo(session, prazo_id, current_user.escritorio_id)
    prazo.excluido_em = utc_now()
    prazo.atualizado_em = utc_now()
    session.add(prazo)
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.prazo_excluido,
            entidade_id=prazo.id,
            resumo=f"Excluiu prazo: {prazo.acao} ({prazo.numero_processo})",
        )
    )
    await session.commit()
    await session.refresh(prazo)
    return await to_prazo_read(session, prazo)
