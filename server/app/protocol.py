"""Реэкспорт общего протокола (копия логики, чтобы Docker-образ сервера был самодостаточным)."""
from __future__ import annotations

import re
from typing import Optional

QR_SCHEME = "qwentory"
SERIAL_BAUD = 9600
WEIGHT_PREFIX = "WEIGHT:"

_WEIGHT_PATTERNS = (
    re.compile(r"^WEIGHT:(-?\d+(?:\.\d+)?)\s*$", re.IGNORECASE),
    re.compile(r"^Weight:\s*(-?\d+(?:\.\d+)?)\s*g", re.IGNORECASE),
    re.compile(r"^(-?\d+(?:\.\d+)?)\s*g\s*$", re.IGNORECASE),
)


def parse_weight_line(line: str) -> Optional[float]:
    text = (line or "").strip()
    if not text:
        return None
    for pattern in _WEIGHT_PATTERNS:
        match = pattern.match(text)
        if match:
            return float(match.group(1))
    return None


def parse_qr_payload(code: str) -> Optional[tuple[str, int]]:
    text = (code or "").strip()
    parts = text.split(":")
    if len(parts) != 3 or parts[0] != QR_SCHEME:
        return None
    kind, raw_id = parts[1], parts[2]
    if kind not in {"item", "type", "box"}:
        return None
    try:
        return kind, int(raw_id)
    except ValueError:
        return None
