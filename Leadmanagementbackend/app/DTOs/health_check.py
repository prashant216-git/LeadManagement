from pydantic import BaseModel


class HealthCheckResponse(BaseModel):

    healthy: bool

    message: str

    latency_ms: int | None = None