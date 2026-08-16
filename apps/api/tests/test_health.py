from app.schemas.health import HealthChecks, HealthResponse


def test_health_response_shape() -> None:
    payload = HealthResponse(
        status="ok",
        app="Agenda Processual API",
        env="development",
        checks=HealthChecks(database="ok", redis="ok"),
    )
    assert payload.status == "ok"
    assert payload.checks.database == "ok"
    assert "Agenda" in payload.app
