"""Чтение весового модуля с Serial и публикация в API /scale."""
from __future__ import annotations

import os
import sys
import threading
import time
from typing import Callable, Optional

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from shared.protocol import SERIAL_BAUD, parse_weight_line  # noqa: E402

from api_client import ApiClient, ApiError  # noqa: E402


class ScaleMonitor:
    def __init__(self, client: ApiClient, port: str = "", on_weight: Optional[Callable[[float], None]] = None):
        self.client = client
        self.port = port
        self.on_weight = on_weight
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.last_weight: Optional[float] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="scale-monitor", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _publish(self, weight: float, line: str) -> None:
        self.last_weight = weight
        if self.on_weight:
            self.on_weight(weight)
        try:
            self.client.post("/scale", {"weight_g": weight, "line": line})
        except ApiError:
            pass

    def _run(self) -> None:
        serial_mod = None
        try:
            import serial  # type: ignore
            serial_mod = serial
        except ImportError:
            serial_mod = None

        while not self._stop.is_set():
            if self.port and serial_mod is not None:
                try:
                    with serial_mod.Serial(self.port, SERIAL_BAUD, timeout=1) as port:
                        while not self._stop.is_set():
                            raw = port.readline()
                            if not raw:
                                continue
                            line = raw.decode("utf-8", errors="replace").strip()
                            weight = parse_weight_line(line)
                            if weight is not None:
                                self._publish(weight, line)
                    continue
                except Exception:
                    time.sleep(1.5)

            try:
                state = self.client.get("/scale")
                weight = state.get("weight_g") if isinstance(state, dict) else None
                if weight is not None:
                    self.last_weight = float(weight)
                    if self.on_weight:
                        self.on_weight(self.last_weight)
            except ApiError:
                pass
            self._stop.wait(1.0)
