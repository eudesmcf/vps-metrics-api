from datetime import datetime

from pydantic import BaseModel, Field


class SystemMetrics(BaseModel):
    timestamp: datetime
    uptime_seconds: float
    cpu_percent: float = Field(ge=0, le=100)
    memory_percent: float = Field(ge=0, le=100)
    memory_total_bytes: int = Field(ge=0)
    memory_available_bytes: int = Field(ge=0)
    disk_path: str
    disk_percent: float = Field(ge=0, le=100)
    disk_total_bytes: int = Field(ge=0)
    disk_free_bytes: int = Field(ge=0)
    network_bytes_sent: int = Field(ge=0)
    network_bytes_received: int = Field(ge=0)


class ContainerMetrics(BaseModel):
    id: str
    name: str
    image: str
    state: str
    status: str
    health: str | None = None
    restart_count: int = Field(ge=0)
    ports: dict[str, list[str]]
    cpu_percent: float | None = Field(default=None, ge=0)
    memory_usage_bytes: int | None = Field(default=None, ge=0)
    memory_limit_bytes: int | None = Field(default=None, ge=0)


class DockerMetrics(BaseModel):
    timestamp: datetime
    containers: list[ContainerMetrics]
    available: bool = True
    error: str | None = None


class AnalyticsMetrics(BaseModel):
    timestamp: datetime
    property_id: str
    start_date: str
    end_date: str
    totals: dict[str, int | float]
    top_sources: list[dict[str, str | int | float]]
    top_pages: list[dict[str, str | int | float]]


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
