from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import or_
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings
from app.core.metrics import record_djen_sync
from app.core.redis import get_redis
from app.core.timeutils import utc_now
from app.integrations.datajud.cnj import so_digitos
from app.integrations.djen.cache import (
    acquire_lock,
    allow_request,
    get_cached,
    release_lock,
    set_cached,
)
from app.integrations.djen.client import DjenError, consultar_comunicacoes
from app.integrations.djen.parse import normalize_item
from app.models.djen_publicacao import DjenPublicacao, DjenStatus
from app.models.escritorio import Escritorio
from app.models.feriado import Feriado
from app.models.processo import Processo
from app.models.user import User
from app.schemas.djen import DjenPublicacaoRead, DjenResumoRead
from app.services.dias_uteis import add_business_days
from app.services.processos import get_processo_by_numero

BRT = ZoneInfo("America/Sao_Paulo")
LOOKBACK_PRIMEIRA_SYNC_DIAS = 7


def today_brt() -> date:
    return datetime.now(BRT).date()


def janela_sync(ultima: datetime | None) -> tuple[date, date]:
    hoje = today_brt()
    if ultima is None:
        return hoje - timedelta(days=LOOKBACK_PRIMEIRA_SYNC_DIAS), hoje
    inicio = ultima.date() - timedelta(days=1)
    if inicio > hoje:
        inicio = hoje - timedelta(days=1)
    return inicio, hoje


async def _feriados_do_escritorio(session: AsyncSession, escritorio_id: UUID) -> set[date]:
    result = await session.exec(select(Feriado.data).where(Feriado.escritorio_id == escritorio_id))
    return set(result.all())


async def sugerir_vencimento(
    session: AsyncSession,
    escritorio_id: UUID,
    data_disponibilizacao: date | None,
    dias: int | None = None,
) -> date | None:
    if data_disponibilizacao is None:
        return None
    settings = get_settings()
    dias_uteis = dias if dias is not None and dias > 0 else settings.djen_prazo_dias_uteis
    feriados = await _feriados_do_escritorio(session, escritorio_id)
    return add_business_days(
        data_disponibilizacao,
        dias_uteis,
        feriados,
    )


async def to_publicacao_read(
    session: AsyncSession,
    item: DjenPublicacao,
) -> DjenPublicacaoRead:
    vencimento = None
    if item.status == DjenStatus.nova and not item.motivo_cancelamento:
        vencimento = await sugerir_vencimento(
            session, item.escritorio_id, item.data_disponibilizacao, item.dias_identificados
        )
    cliente = None
    if item.processo_id:
        processo = await session.get(Processo, item.processo_id)
        if processo is not None:
            cliente = processo.cliente
    return DjenPublicacaoRead(
        id=item.id,
        processo_id=item.processo_id,
        prazo_id=item.prazo_id,
        numero_processo=item.numero_processo,
        cliente=cliente,
        tribunal=item.tribunal,
        tipo_comunicacao=item.tipo_comunicacao,
        tipo_documento=item.tipo_documento,
        nome_classe=item.nome_classe,
        orgao=item.orgao,
        texto=item.texto,
        link=item.link,
        destinatarios=item.destinatarios,
        dias_identificados=item.dias_identificados,
        data_disponibilizacao=item.data_disponibilizacao,
        vencimento_sugerido=vencimento,
        status=item.status.value,
        motivo_cancelamento=item.motivo_cancelamento,
        sincronizado_em=item.sincronizado_em,
        criado_em=item.criado_em,
    )


async def list_publicacoes(
    session: AsyncSession,
    escritorio_id: UUID,
    *,
    status: DjenStatus | None = None,
    processo_id: UUID | None = None,
    busca: str | None = None,
) -> list[DjenPublicacao]:
    query = select(DjenPublicacao).where(DjenPublicacao.escritorio_id == escritorio_id)
    if status is not None:
        query = query.where(DjenPublicacao.status == status)
    if processo_id is not None:
        query = query.where(DjenPublicacao.processo_id == processo_id)
    if busca and busca.strip():
        term = f"%{busca.strip()}%"
        query = query.where(
            or_(
                DjenPublicacao.numero_processo.ilike(term),
                DjenPublicacao.tribunal.ilike(term),
                DjenPublicacao.orgao.ilike(term),
                DjenPublicacao.texto.ilike(term),
                DjenPublicacao.destinatarios.ilike(term),
                DjenPublicacao.nome_classe.ilike(term),
            )
        )
    query = query.order_by(
        col(DjenPublicacao.data_disponibilizacao).desc(),
        col(DjenPublicacao.criado_em).desc(),
    )
    result = await session.exec(query)
    return list(result.all())


async def count_novas(session: AsyncSession, escritorio_id: UUID) -> int:
    items = await list_publicacoes(session, escritorio_id, status=DjenStatus.nova)
    return sum(1 for item in items if not item.motivo_cancelamento)


async def resumo(session: AsyncSession, escritorio_id: UUID) -> DjenResumoRead:
    all_items = await list_publicacoes(session, escritorio_id)
    novas = sum(1 for item in all_items if item.status == DjenStatus.nova and not item.motivo_cancelamento)
    com_prazo = sum(1 for item in all_items if item.status == DjenStatus.prazo_criado)
    ignoradas = sum(1 for item in all_items if item.status == DjenStatus.ignorada or item.motivo_cancelamento)
    return DjenResumoRead(
        novas=novas,
        com_prazo=com_prazo,
        ignoradas=ignoradas,
        total=len(all_items),
    )


async def _get_by_djen_id(
    session: AsyncSession,
    escritorio_id: UUID,
    djen_id: str,
) -> DjenPublicacao | None:
    result = await session.exec(
        select(DjenPublicacao).where(
            DjenPublicacao.escritorio_id == escritorio_id,
            DjenPublicacao.djen_id == djen_id,
        )
    )
    return result.first()


def _apply_normalized(
    row: DjenPublicacao, parsed: dict[str, Any], processo_id: UUID | None
) -> None:
    row.processo_id = processo_id
    row.hash = parsed.get("hash")
    row.numero_processo = parsed["numero_processo"]
    row.numero_processo_digitos = parsed["numero_processo_digitos"]
    row.tribunal = parsed.get("tribunal")
    row.tipo_comunicacao = parsed["tipo_comunicacao"]
    row.tipo_documento = parsed.get("tipo_documento")
    row.nome_classe = parsed.get("nome_classe")
    row.orgao = parsed.get("orgao")
    row.texto = parsed.get("texto")
    row.link = parsed.get("link")
    row.destinatarios = parsed.get("destinatarios")
    row.dias_identificados = parsed.get("dias_identificados")
    row.data_disponibilizacao = parsed.get("data_disponibilizacao")
    row.motivo_cancelamento = parsed.get("motivo_cancelamento")
    row.sincronizado_em = utc_now()
    row.atualizado_em = utc_now()


async def upsert_items(
    session: AsyncSession,
    escritorio_id: UUID,
    items: list[dict[str, Any]],
    processo: Processo | None = None,
) -> int:
    """Persiste itens do DJEN associando ao processo quando disponível. Retorna quantos eram novos."""
    criados = 0
    now = utc_now()
    for raw in items:
        parsed = normalize_item(raw)
        if parsed is None:
            continue
        if processo is not None and parsed["numero_processo_digitos"] != so_digitos(processo.numero_processo):
            continue

        target_proc_id = processo.id if processo is not None else None
        if target_proc_id is None:
            found = await get_processo_by_numero(
                session, parsed["numero_processo_digitos"], escritorio_id=escritorio_id
            )
            if found is not None:
                target_proc_id = found.id

        existing = await _get_by_djen_id(session, escritorio_id, parsed["djen_id"])
        if existing is None:
            row = DjenPublicacao(
                escritorio_id=escritorio_id,
                processo_id=target_proc_id,
                djen_id=parsed["djen_id"],
                status=DjenStatus.nova,
                criado_em=now,
            )
            _apply_normalized(row, parsed, target_proc_id)
            session.add(row)
            criados += 1
            continue
        _apply_normalized(
            existing,
            parsed,
            target_proc_id if existing.processo_id is None else existing.processo_id,
        )
        session.add(existing)
    return criados


@dataclass
class SyncResult:
    ok: bool
    cache: bool = False
    criados: int = 0
    mensagem: str | None = None


async def sincronizar_processo(
    session: AsyncSession,
    processo: Processo,
    *,
    force: bool = False,
) -> SyncResult:
    settings = get_settings()
    if not settings.djen_enabled:
        return SyncResult(ok=False, mensagem="Consulta ao DJEN desabilitada")

    digitos = so_digitos(processo.numero_processo)
    if len(digitos) != 20:
        return SyncResult(ok=False, mensagem="Número de processo inválido para o DJEN")

    redis = await get_redis()
    inicio, fim = janela_sync(processo.djen_sincronizado_em)
    cache_payload = {
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "items": [],
    }

    if redis is not None and not force:
        cached = await get_cached(redis, digitos)
        if cached is not None:
            await upsert_items(session, processo.escritorio_id, cached.get("items") or [], processo)
            processo.djen_sincronizado_em = utc_now()
            session.add(processo)
            await session.commit()
            return SyncResult(ok=True, cache=True)

    if redis is not None:
        if not await allow_request(redis):
            return SyncResult(
                ok=False,
                mensagem="Muitas consultas ao DJEN. Tente de novo em instantes.",
            )
        if not await acquire_lock(redis, digitos):
            return SyncResult(
                ok=False,
                mensagem="Sincronização já em andamento para este processo.",
            )

    try:
        items = await consultar_comunicacoes(
            numero_processo_digitos=digitos,
            data_inicio=inicio,
            data_fim=fim,
        )
        criados = await upsert_items(session, processo.escritorio_id, items, processo)
        processo.djen_sincronizado_em = utc_now()
        session.add(processo)
        await session.commit()
        cache_payload["items"] = items
        if redis is not None:
            await set_cached(redis, digitos, cache_payload, empty=len(items) == 0)
        record_djen_sync(ok=True, criados=criados)
        return SyncResult(ok=True, criados=criados)
    except DjenError as exc:
        record_djen_sync(ok=False, criados=0)
        return SyncResult(ok=False, mensagem=str(exc))
    finally:
        if redis is not None:
            await release_lock(redis, digitos)


async def sincronizar_escritorio(session: AsyncSession, escritorio_id: UUID) -> SyncResult:
    result = await session.exec(select(Processo).where(Processo.escritorio_id == escritorio_id))
    processos = list(result.all())
    criados = 0
    erros = 0
    for processo in processos:
        sync = await sincronizar_processo(session, processo, force=True)
        criados += sync.criados
        if not sync.ok:
            erros += 1

    # Radar automático por advogados cadastrados no escritório
    users_res = await session.exec(
        select(User).where(User.escritorio_id == escritorio_id, User.ativo == True)
    )
    users = list(users_res.all())
    hoje = today_brt()
    inicio = hoje - timedelta(days=LOOKBACK_PRIMEIRA_SYNC_DIAS)
    for u in users:
        nome = u.nome.strip()
        if len(nome.split()) >= 2:
            try:
                items = await consultar_comunicacoes(
                    nome_advogado=nome,
                    data_inicio=inicio,
                    data_fim=hoje,
                )
                novos = await upsert_items(session, escritorio_id, items)
                criados += novos
                await session.commit()
            except Exception:
                pass

    return SyncResult(
        ok=erros == 0,
        criados=criados,
        mensagem=None if erros == 0 else f"{erros} processo(s) com falha na sync",
    )


async def sincronizar_todos() -> SyncResult:
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        result = await session.exec(select(Escritorio))
        escritorios = list(result.all())
        criados = 0
        erros = 0
        for escritorio in escritorios:
            sync = await sincronizar_escritorio(session, escritorio.id)
            criados += sync.criados
            if not sync.ok:
                erros += 1
        return SyncResult(
            ok=erros == 0,
            criados=criados,
            mensagem=None if erros == 0 else f"{erros} escritório(s) com falha na sync",
        )


async def ignorar_publicacao(session: AsyncSession, item: DjenPublicacao) -> DjenPublicacao:
    item.status = DjenStatus.ignorada
    item.atualizado_em = utc_now()
    session.add(item)
    return item


async def vincular_ao_prazo(
    session: AsyncSession,
    item: DjenPublicacao,
    prazo_id: UUID,
) -> None:
    if item.status == DjenStatus.prazo_criado and item.prazo_id is not None:
        return
    item.prazo_id = prazo_id
    item.status = DjenStatus.prazo_criado
    item.atualizado_em = utc_now()
    session.add(item)
