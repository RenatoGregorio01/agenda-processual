from app.schemas.auth import LoginRequest, TokenResponse, UserRead
from app.schemas.health import HealthResponse
from app.schemas.prazo import PrazoCreate, PrazoRead, PrazoUpdate

__all__ = [
    "HealthResponse",
    "LoginRequest",
    "PrazoCreate",
    "PrazoRead",
    "PrazoUpdate",
    "TokenResponse",
    "UserRead",
]
