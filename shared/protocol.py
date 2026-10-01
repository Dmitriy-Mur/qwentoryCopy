"""Единый протокол весов и QR для сервера, десктопа, моста и прошивки.

Вес по Serial (9600 8N1), одна строка:
    WEIGHT:<граммы>
Дополнительно принимаются человекочитаемые строки Arduino:
    Weight: 12.34 g

QR-этикетка:
    qwentory:item:<item_id>
    qwentory:type:<item_type_id>
    qwentory:box:<box_id>
"""
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


def format_weight_line(weight_g: float) -> str:
    return f"{WEIGHT_PREFIX}{weight_g:.2f}"


def make_qr_payload(kind: str, entity_id: int) -> str:
    if kind not in {"item", "type", "box"}:
        raise ValueError(f"Unknown QR kind: {kind}")
    return f"{QR_SCHEME}:{kind}:{int(entity_id)}"


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
