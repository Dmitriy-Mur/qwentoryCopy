"""Генерация QR-этикеток в формате qwentory:<kind>:<id>."""
from __future__ import annotations

import io
import os
import sys
from typing import Optional

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from shared.protocol import make_qr_payload  # noqa: E402


def qr_payload(kind: str, entity_id: int) -> str:
    return make_qr_payload(kind, entity_id)


def qr_png_bytes(payload: str) -> bytes:
    try:
        import qrcode
    except ImportError as error:
        raise RuntimeError("Установите пакет qrcode: pip install 'qrcode[pil]'") from error

    image = qrcode.make(payload)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
