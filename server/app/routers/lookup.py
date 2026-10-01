from fastapi import APIRouter, HTTPException

from app.protocol import parse_qr_payload
from app.routers.boxes import get_box, get_box_contents
from app.routers.item_types import get_item_type
from app.routers.items import get_item


router = APIRouter(tags=["Lookup"])


@router.get("/lookup")
def lookup(code: str):
    parsed = parse_qr_payload(code)
    if parsed is None:
        raise HTTPException(
            status_code=400,
            detail="QR must look like qwentory:item:<id>, qwentory:type:<id> or qwentory:box:<id>",
        )

    kind, entity_id = parsed

    if kind == "item":
        return {"kind": "item", "item": get_item(entity_id)}
    if kind == "type":
        return {"kind": "type", "item_type": get_item_type(entity_id)}
    return {
        "kind": "box",
        "box": get_box(entity_id),
        "contents": get_box_contents(entity_id),
    }
