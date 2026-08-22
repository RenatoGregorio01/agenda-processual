from prometheus_client import REGISTRY

from app.core.metrics import record_alertas_result, record_audit_purge, record_djen_sync


def _counter_value(name: str) -> float:
    for metric in REGISTRY.collect():
        if metric.name != name:
            continue
        for sample in metric.samples:
            if sample.name in {name, f"{name}_total"}:
                return float(sample.value)
    return 0.0


def test_record_alertas_result_increments_counters() -> None:
    before_env = _counter_value("agenda_alertas_enviados")
    before_err = _counter_value("agenda_alertas_erros")
    record_alertas_result(candidatos=3, enviados=2, erros=1, ignorados=0)
    assert _counter_value("agenda_alertas_enviados") == before_env + 2
    assert _counter_value("agenda_alertas_erros") == before_err + 1


def test_record_audit_purge_increments_counter() -> None:
    before = _counter_value("agenda_audit_purge_deleted")
    record_audit_purge(deleted=4)
    record_audit_purge(deleted=0)
    assert _counter_value("agenda_audit_purge_deleted") == before + 4


def test_record_djen_sync_increments_counters() -> None:
    before_ok = _counter_value("agenda_djen_sync_ok")
    before_new = _counter_value("agenda_djen_publicacoes_novas")
    record_djen_sync(ok=True, criados=2)
    record_djen_sync(ok=False, criados=0)
    assert _counter_value("agenda_djen_sync_ok") == before_ok + 1
    assert _counter_value("agenda_djen_publicacoes_novas") == before_new + 2
