from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.protocol import parse_weight_line


router = APIRouter(prefix="/scale", tags=["Scale"])

_latest: dict | None = None


class ScaleReading(BaseModel):
    weight_g: float | None = None
    line: str | None = None


class ScaleState(BaseModel):
    weight_g: float | None = None
    updated_at: datetime | None = None
    source: str = "none"


@router.get("", response_model=ScaleState)
def get_scale():
    if _latest is None:
        return ScaleState()
    return ScaleState(**_latest)


@router.post("", response_model=ScaleState)
def post_scale(reading: ScaleReading):
    global _latest

    weight = reading.weight_g
    if weight is None and reading.line:
        weight = parse_weight_line(reading.line)
    if weight is None:
        raise HTTPException(
            status_code=400,
            detail="Provide weight_g or a parseable serial line",
        )

    _latest = {
        "weight_g": float(weight),
        "updated_at": datetime.now(timezone.utc),
        "source": "serial" if reading.line else "api",
    }
    return ScaleState(**_latest)


@router.delete("")
def clear_scale():
    global _latest
    _latest = None
    return {"message": "Scale reading cleared"}
