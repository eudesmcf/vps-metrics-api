from datetime import datetime

import psutil

from src.config import get_settings
from src.models.metrics import SystemMetrics


def collect_system_metrics(disk_path: str = "/") -> SystemMetrics:
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(disk_path)
    network = psutil.net_io_counters()
    return SystemMetrics(
        timestamp=get_settings().now(),
        uptime_seconds=max(0.0, __import__("time").time() - psutil.boot_time()),
        cpu_percent=psutil.cpu_percent(interval=0.1),
        memory_percent=memory.percent,
        memory_total_bytes=memory.total,
        memory_available_bytes=memory.available,
        disk_path=disk_path,
        disk_percent=disk.percent,
        disk_total_bytes=disk.total,
        disk_free_bytes=disk.free,
        network_bytes_sent=network.bytes_sent,
        network_bytes_received=network.bytes_recv,
    )
