from prometheus_client import REGISTRY

from app.core.metrics import record_alertas_result


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
