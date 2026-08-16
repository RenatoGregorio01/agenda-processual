from pydantic import BaseModel


class HealthChecks(BaseModel):
    database: str
    redis: str


class HealthResponse(BaseModel):
    status: str
    app: str
    env: str
    checks: HealthChecks
