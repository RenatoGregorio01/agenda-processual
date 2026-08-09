from app.core.config import Settings
from app.schemas.health import HealthResponse


def test_health_response_shape() -> None:
    settings = Settings()
    payload = HealthResponse(status="ok", app=settings.app_name, env=settings.app_env)
    assert payload.status == "ok"
    assert "Agenda" in payload.app
