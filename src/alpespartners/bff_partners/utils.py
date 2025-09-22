import time
from datetime import datetime

def time_millis() -> int:
    """Retorna timestamp en milisegundos"""
    return int(time.time() * 1000)

def datetime_to_iso(dt: datetime) -> str:
    """Convierte datetime a string ISO"""
    return dt.isoformat()

def iso_to_datetime(iso_string: str) -> datetime:
    """Convierte string ISO a datetime"""
    return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
