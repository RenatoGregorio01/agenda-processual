from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.redis import get_redis
from app.core.timeutils import utc_now
from app.integrations.datajud import alias_do_cnj
from app.integrations.datajud.cache import (
    acquire_lock,
    allow_request,
    get_cached,
    release_lock,
    set_cached,
)
from app.integrations.datajud.client import DatajudError, consultar_processo
from app.integrations.datajud.cnj import CnjError
from app.models.processo import Processo
from app.models.processo_andamento import ProcessoAndamento
from app.schemas.processo import DatajudAndamentoRead, DatajudSyncRead

MAX_ANDAMENTOS = 20

STATUS_NUNCA = "nunca_consultado"
STATUS_OK = "ok"
STATUS_INDISPONIVEL = "indisponivel"
STATUS_NAO_SUPORTADO = "tribunal_nao_suportado"
STATUS_ERRO = "erro"
STATUS_NAO_CONFIGURADO = "nao_configurado"
STATUS_LIMITE = "limite"


def _parse_data_hora(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None) if value.tzinfo else value
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed


def _andamentos_from_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    raw = source.get("movimentos") or []
    if not isinstance(raw, list):
        return []
    items: list[dict[str, Any]] = []
    for movimento in raw:
        if not isinstance(movimento, dict):
            continue
        nome = str(movimento.get("nome") or "").strip()
        if not nome:
            continue
        codigo = movimento.get("codigo")
        items.append(
            {
                "data_hora": _parse_data_hora(movimento.get("dataHora")),
                "codigo": int(codigo) if isinstance(codigo, int) else None,
                "nome": nome[:255],
            }
        )
    items.sort(key=lambda item: item["data_hora"] or datetime.min, reverse=True)
    return items[:MAX_ANDAMENTOS]


def _payload_from_source(alias: str, source: dict[str, Any] | None) -> dict[str, Any]:
    if source is None:
        return {
            "status": STATUS_INDISPONIVEL,
            "tribunal": alias,
            "grau": None,
            "classe": None,
            "orgao": None,
            "mensagem": "Andamentos do tribunal indisponíveis",
            "andamentos": [],
        }

    classe = source.get("classe") if isinstance(source.get("classe"), dict) else {}
    orgao = source.get("orgaoJulgador") if isinstance(source.get("orgaoJulgador"), dict) else {}
    return {
        "status": STATUS_OK,
        "tribunal": str(source.get("tribunal") or alias),
        "grau": str(source.get("grau") or "") or None,
        "classe": str(classe.get("nome") or "") or None,
        "orgao": str(orgao.get("nome") or "") or None,
        "mensagem": None,
        "andamentos": _andamentos_from_source(source),
    }


def _jsonable_payload(payload: dict[str, Any]) -> dict[str, Any]:
    andamentos = []
    for item in payload.get("andamentos") or []:
        data_hora = item.get("data_hora")
        andamentos.append(
            {
                "data_hora": (
                    data_hora.isoformat() if isinstance(data_hora, datetime) else data_hora
                ),
                "codigo": item.get("codigo"),
                "nome": item["nome"],
            }
        )
    return {**payload, "andamentos": andamentos}


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    andamentos = []
    for item in payload.get("andamentos") or []:
        andamentos.append(
            {
                "data_hora": _parse_data_hora(item.get("data_hora")),
                "codigo": item.get("codigo"),
                "nome": item["nome"],
            }
        )
    return {**payload, "andamentos": andamentos}


async def _replace_andamentos(
    session: AsyncSession,
    processo_id: UUID,
    andamentos: list[dict[str, Any]],
) -> None:
    result = await session.exec(
        select(ProcessoAndamento).where(ProcessoAndamento.processo_id == processo_id)
    )
    for item in result.all():
        await session.delete(item)

    for ordem, andamento in enumerate(andamentos):
        session.add(
            ProcessoAndamento(
                processo_id=processo_id,
                data_hora=andamento.get("data_hora"),
                codigo=andamento.get("codigo"),
                nome=andamento["nome"],
                ordem=ordem,
            )
        )


async def _apply_payload(
    session: AsyncSession,
    processo: Processo,
    payload: dict[str, Any],
) -> None:
    processo.datajud_status = payload["status"]
    processo.datajud_sincronizado_em = utc_now()
    processo.datajud_tribunal = payload.get("tribunal")
    processo.datajud_grau = payload.get("grau")
    processo.datajud_classe = payload.get("classe")
    processo.datajud_orgao = payload.get("orgao")
    processo.datajud_mensagem = payload.get("mensagem")
    session.add(processo)
    await _replace_andamentos(session, processo.id, payload.get("andamentos") or [])
    await session.commit()
    await session.refresh(processo)


async def list_andamentos(
    session: AsyncSession,
    processo_id: UUID,
) -> list[ProcessoAndamento]:
    result = await session.exec(
        select(ProcessoAndamento)
        .where(ProcessoAndamento.processo_id == processo_id)
        .order_by(col(ProcessoAndamento.ordem).asc())
    )
    return list(result.all())


async def to_datajud_read(
    session: AsyncSession,
    processo: Processo,
    *,
    cache: bool = False,
) -> DatajudSyncRead:
    andamentos = await list_andamentos(session, processo.id)
    status = processo.datajud_status or STATUS_NUNCA
    return DatajudSyncRead(
        status=status,
        sincronizado_em=processo.datajud_sincronizado_em,
        tribunal=processo.datajud_tribunal,
        grau=processo.datajud_grau,
        classe=processo.datajud_classe,
        orgao=processo.datajud_orgao,
        mensagem=processo.datajud_mensagem,
        cache=cache,
        andamentos=[
            DatajudAndamentoRead.model_validate(item, from_attributes=True)
            for item in andamentos
        ],
    )


async def consultar_existencia_datajud(numero: str) -> dict[str, Any]:
    """Consulta a Datajud sem gravar no banco. Reutiliza o cache Redis."""
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.datajud_api_key.strip():
        return {"status": STATUS_NAO_CONFIGURADO, "encontrado": None}

    try:
        digitos, _alias = alias_do_cnj(numero)
    except CnjError as exc:
        return {
            "status": STATUS_NAO_SUPORTADO,
            "encontrado": None,
            "mensagem": str(exc),
        }

    redis = await get_redis()
    if redis is not None:
        cached = await get_cached(redis, digitos)
        if cached is not None:
            encontrado = cached.get("status") == STATUS_OK
            return {
                "status": cached.get("status") or STATUS_INDISPONIVEL,
                "encontrado": encontrado,
                "cache": True,
            }
        if not await allow_request(redis):
            return {
                "status": STATUS_LIMITE,
                "encontrado": None,
                "mensagem": "Muitas consultas ao tribunal. Tente de novo em instantes.",
            }

    try:
        _, alias, source = await consultar_processo(numero)
        payload = _payload_from_source(alias, source)
        if redis is not None:
            await set_cached(
                redis,
                digitos,
                _jsonable_payload(payload),
                empty=payload["status"] != STATUS_OK,
            )
        return {
            "status": payload["status"],
            "encontrado": payload["status"] == STATUS_OK,
        }
    except DatajudError as exc:
        return {"status": STATUS_ERRO, "encontrado": None, "mensagem": str(exc)}


async def sincronizar_datajud(
    session: AsyncSession,
    processo: Processo,
    *,
    force: bool = False,
) -> DatajudSyncRead:
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.datajud_api_key.strip():
        processo.datajud_status = STATUS_NAO_CONFIGURADO
        processo.datajud_mensagem = "Consulta ao tribunal não configurada"
        processo.datajud_sincronizado_em = utc_now()
        session.add(processo)
        await session.commit()
        return await to_datajud_read(session, processo)

    try:
        digitos, alias = alias_do_cnj(processo.numero_processo)
    except CnjError as exc:
        payload = {
            "status": STATUS_NAO_SUPORTADO,
            "tribunal": None,
            "grau": None,
            "classe": None,
            "orgao": None,
            "mensagem": str(exc),
            "andamentos": [],
        }
        await _apply_payload(session, processo, payload)
        return await to_datajud_read(session, processo)

    redis = await get_redis()
    if redis is not None and not force:
        cached = await get_cached(redis, digitos)
        if cached is not None:
            await _apply_payload(session, processo, _normalize_payload(cached))
            return await to_datajud_read(session, processo, cache=True)

    locked = False
    if redis is not None:
        if not await allow_request(redis):
            current = await to_datajud_read(session, processo)
            current.status = STATUS_LIMITE
            current.mensagem = "Muitas consultas ao tribunal. Tente de novo em instantes."
            return current
        locked = await acquire_lock(redis, digitos)
        if not locked:
            for _ in range(10):
                await asyncio.sleep(0.4)
                cached = await get_cached(redis, digitos)
                if cached is not None:
                    await _apply_payload(session, processo, _normalize_payload(cached))
                    return await to_datajud_read(session, processo, cache=True)

    try:
        _, alias, source = await consultar_processo(processo.numero_processo)
        payload = _payload_from_source(alias, source)
        if redis is not None:
            await set_cached(
                redis,
                digitos,
                _jsonable_payload(payload),
                empty=payload["status"] != STATUS_OK,
            )
        await _apply_payload(session, processo, payload)
        return await to_datajud_read(session, processo)
    except DatajudError as exc:
        processo.datajud_status = STATUS_ERRO
        processo.datajud_mensagem = str(exc)
        processo.datajud_sincronizado_em = utc_now()
        session.add(processo)
        await session.commit()
        return await to_datajud_read(session, processo)
    finally:
        if redis is not None and locked:
            await release_lock(redis, digitos)
