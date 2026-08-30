from datetime import datetime

import docker
from docker.errors import DockerException

from src.config import get_settings
from src.models.metrics import ContainerMetrics, DockerMetrics


def _container_stats(container) -> tuple[float | None, int | None, int | None]:
    try:
        stats = container.stats(stream=False)
        memory = stats.get("memory_stats", {})
        usage = memory.get("usage")
        limit = memory.get("limit")
        cpu_stats = stats.get("cpu_stats", {})
        previous = stats.get("precpu_stats", {})
        cpu_delta = cpu_stats.get("cpu_usage", {}).get("total_usage", 0) - previous.get("cpu_usage", {}).get("total_usage", 0)
        system_delta = cpu_stats.get("system_cpu_usage", 0) - previous.get("system_cpu_usage", 0)
        online_cpus = cpu_stats.get("online_cpus") or len(cpu_stats.get("cpu_usage", {}).get("percpu_usage", []) or []) or 1
        cpu = (cpu_delta / system_delta * online_cpus * 100) if system_delta > 0 else 0.0
        return cpu, usage, limit
    except DockerException:
        return None, None, None


def collect_docker_metrics(docker_host: str | None = None) -> DockerMetrics:
    try:
        client = docker.DockerClient(base_url=docker_host) if docker_host else docker.from_env()
        containers = []
        for container in client.containers.list(all=True):
            attrs = container.attrs
            state = attrs.get("State", {})
            cpu, usage, limit = _container_stats(container) if state.get("Status") == "running" else (None, None, None)
            containers.append(ContainerMetrics(
                id=container.short_id,
                name=container.name,
                image=attrs.get("Config", {}).get("Image", ""),
                state=state.get("Status", container.status),
                status=container.status,
                health=state.get("Health", {}).get("Status"),
                restart_count=attrs.get("RestartCount", 0),
                ports=attrs.get("NetworkSettings", {}).get("Ports", {}) or {},
                cpu_percent=cpu,
                memory_usage_bytes=usage,
                memory_limit_bytes=limit,
            ))
        client.close()
        return DockerMetrics(timestamp=get_settings().now(), containers=containers)
    except DockerException as exc:
        return DockerMetrics(timestamp=get_settings().now(), containers=[], available=False, error=str(exc))
