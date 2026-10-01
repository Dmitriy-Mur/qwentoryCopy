"""Настройки десктопа: адрес API и serial-порт весов."""
import os


def api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def serial_port() -> str:
    return os.getenv("SERIAL_PORT", os.getenv("SERIAL_DEVICE", ""))
