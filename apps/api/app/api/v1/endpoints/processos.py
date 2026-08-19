from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_permission
from app.core.database import get_session
from app.core.permissions import Permission
from app.core.tenant import get_owned
from app.core.timeutils import utc_now
from app.integrations.datajud.cnj import CnjError, so_digitos, validar_cnj
from app.models.audit_log import AuditAction
from app.models.processo import Processo
from app.models.user import User
from app.schemas.audit import AuditLogRead
from app.schemas.djen import DjenSyncRead
from app.schemas.prazo import PrazoRead
from app.schemas.processo import (
    DatajudSyncRead,
    ProcessoDetail,
    ProcessoRead,
    ProcessoUpdate,
    ProcessoValidarRead,
)
from app.services.alertas import to_prazo_read
from app.services.audit import montar_auditoria
from app.services.datajud import (
    consultar_existencia_datajud,
    sincronizar_datajud,
    to_datajud_read,
)
from app.services.djen import (
    list_publicacoes,
    to_publicacao_read,
)
from app.services.djen import (
    sincronizar_processo as sincronizar_djen_processo,
)
from app.services.processos import (
    count_prazos_processo,
    get_processo_by_numero,
    list_historico_processo,
    list_prazos_processo,
)

router = APIRouter()


async def _to_processo_read(session: AsyncSession, processo: Processo) -> ProcessoRead:
    return ProcessoRead(
        id=processo.id,
        numero_processo=processo.numero_processo,
        cliente=processo.cliente,
        criado_em=processo.criado_em,
        atualizado_em=processo.atualizado_em,
        prazos_count=await count_prazos_processo(session, processo.id),
    )


async def _to_prazo_read(session: AsyncSession, prazo) -> PrazoRead:
    return await to_prazo_read(session, prazo)


async def _detail(session: AsyncSession, processo: Processo) -> ProcessoDetail:
    prazos = await list_prazos_processo(session, processo.id, incluir_excluidos=True)
    historico = await list_historico_processo(session, processo)
    prazo_reads = [await _to_prazo_read(session, prazo) for prazo in prazos]
    return ProcessoDetail(
        processo=await _to_processo_read(session, processo),
        prazos=prazo_reads,
        historico=[
            AuditLogRead.model_validate(item, from_attributes=True) for item in historico
        ],
        datajud=await to_datajud_read(session, processo),
        djen=[
            await to_publicacao_read(session, item)
            for item in await list_publicacoes(
                session, processo.escritorio_id, processo_id=processo.id
            )
        ],
    )


@router.get(
    "",
    response_model=list[ProcessoRead],
)
async def listar_processos(
    q: str | None = Query(default=None, max_length=120),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> list[ProcessoRead]:
    query = (
        select(Processo)
        .where(Processo.escritorio_id == current_user.escritorio_id)
        .order_by(col(Processo.atualizado_em).desc())
    )
    if q and q.strip():
        term = f"%{q.strip().lower()}%"
        query = query.where(
            col(Processo.numero_processo).ilike(term) | col(Processo.cliente).ilike(term)
        )
    result = await session.exec(query.limit(100))
    processos = list(result.all())
    return [await _to_processo_read(session, item) for item in processos]


@router.get(
    "/validar",
    response_model=ProcessoValidarRead,
)
async def validar_numero_processo(
    numero: str = Query(..., min_length=1, max_length=64),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> ProcessoValidarRead:
    async def _cadastrado(processo: Processo | None) -> ProcessoValidarRead:
        if processo is None:
            return ProcessoValidarRead()
        return ProcessoValidarRead(
            cadastrado=True,
            processo_id=processo.id,
            cliente=processo.cliente,
            prazos_count=await count_prazos_processo(session, processo.id),
        )

    digitos = so_digitos(numero)
    if len(digitos) < 20:
        existing = await get_processo_by_numero(
            session, numero, escritorio_id=current_user.escritorio_id
        )
        local = await _cadastrado(existing)
        local.incompleto = True
        return local

    try:
        mascarado = validar_cnj(numero)
    except CnjError as exc:
        return ProcessoValidarRead(valido=False, mensagem=str(exc))

    existing = await get_processo_by_numero(
        session, mascarado, escritorio_id=current_user.escritorio_id
    )
    local = await _cadastrado(existing)
    local.valido = True
    local.mascarado = mascarado

    consulta = await consultar_existencia_datajud(mascarado)
    encontrado = consulta.get("encontrado")
    if encontrado is True:
        local.datajud = "encontrado"
        local.datajud_mensagem = "Processo encontrado na base pública do tribunal."
    elif encontrado is False:
        local.datajud = "nao_encontrado"
        local.datajud_mensagem = (
            "Este número não aparece na base pública. Pode estar em sigilo, "
            "ainda não indexado ou ser uma numeração interna. Você pode salvar mesmo assim."
        )
    elif consulta.get("status") in {"limite", "erro"}:
        local.datajud = str(consulta["status"])
        local.datajud_mensagem = "Não foi possível consultar a base pública agora."

    return local


@router.get(
    "/by-numero/{numero_processo:path}",
    response_model=ProcessoDetail,
)
async def obter_processo_por_numero(
    numero_processo: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> ProcessoDetail:
    processo = await get_processo_by_numero(
        session, numero_processo, escritorio_id=current_user.escritorio_id
    )
    if processo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processo não encontrado",
        )
    return await _detail(session, processo)


@router.get(
    "/{processo_id}",
    response_model=ProcessoDetail,
)
async def obter_processo(
    processo_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> ProcessoDetail:
    processo = await get_owned(
        session,
        Processo,
        processo_id,
        current_user.escritorio_id,
        detail="Processo não encontrado",
    )
    return await _detail(session, processo)


@router.patch("/{processo_id}", response_model=ProcessoRead)
async def atualizar_processo(
    processo_id: UUID,
    payload: ProcessoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_alterar)),
) -> ProcessoRead:
    processo = await get_owned(
        session,
        Processo,
        processo_id,
        current_user.escritorio_id,
        detail="Processo não encontrado",
    )

    data = payload.model_dump(exclude_unset=True)
    if "cliente" in data and data["cliente"] is not None:
        processo.cliente = data["cliente"].strip()
        prazos = await list_prazos_processo(session, processo.id, incluir_excluidos=True)
        for prazo in prazos:
            prazo.cliente = processo.cliente
            session.add(prazo)

    processo.atualizado_em = utc_now()
    session.add(processo)
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.processo_atualizado,
            entidade="processo",
            entidade_id=processo.id,
            resumo=f"Atualizou processo {processo.numero_processo}",
        )
    )
    await session.commit()
    await session.refresh(processo)
    return await _to_processo_read(session, processo)


@router.post(
    "/{processo_id}/datajud/sync",
    response_model=DatajudSyncRead,
)
async def sincronizar_andamentos_datajud(
    processo_id: UUID,
    force: bool = Query(default=False),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> DatajudSyncRead:
    processo = await get_owned(
        session,
        Processo,
        processo_id,
        current_user.escritorio_id,
        detail="Processo não encontrado",
    )
    return await sincronizar_datajud(session, processo, force=force)


@router.post(
    "/{processo_id}/djen/sync",
    response_model=DjenSyncRead,
)
async def sincronizar_publicacoes_djen(
    processo_id: UUID,
    force: bool = Query(default=False),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> DjenSyncRead:
    processo = await get_owned(
        session,
        Processo,
        processo_id,
        current_user.escritorio_id,
        detail="Processo não encontrado",
    )
    result = await sincronizar_djen_processo(session, processo, force=force)
    items = await list_publicacoes(
        session, current_user.escritorio_id, processo_id=processo.id
    )
    return DjenSyncRead(
        ok=result.ok,
        cache=result.cache,
        criados=result.criados,
        mensagem=result.mensagem,
        publicacoes=[await to_publicacao_read(session, item) for item in items],
    )
