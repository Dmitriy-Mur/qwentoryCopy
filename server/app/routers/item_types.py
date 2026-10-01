import sqlite3

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database import get_db


router = APIRouter(
    prefix="/item-types",
    tags=["Item types"]
)


class ItemTypeCreate(BaseModel):
    name: str
    weight_g: int | None = Field(default=None, ge=0)


class ItemTypeUpdate(BaseModel):
    name: str | None = None
    weight_g: int | None = Field(default=None, ge=0)


@router.get("")
def get_item_types():
    with get_db() as db:
        rows = db.execute(
            """
            SELECT item_type_id, item_type_name, weight_g
            FROM item_type
            ORDER BY item_type_id
            """
        ).fetchall()

    return [
        {
            "id": row["item_type_id"],
            "name": row["item_type_name"],
            "weight_g": row["weight_g"]
        }
        for row in rows
    ]


@router.get("/{item_type_id}")
def get_item_type(item_type_id: int):
    with get_db() as db:
        row = db.execute(
            """
            SELECT item_type_id, item_type_name, weight_g
            FROM item_type
            WHERE item_type_id = ?
            """,
            (item_type_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Item type not found"
        )

    return {
        "id": row["item_type_id"],
        "name": row["item_type_name"],
        "weight_g": row["weight_g"]
    }


@router.post("")
def create_item_type(item_type: ItemTypeCreate):
    try:
        with get_db() as db:
            cursor = db.execute(
                """
                INSERT INTO item_type (item_type_name, weight_g)
                VALUES (?, ?)
                """,
                (item_type.name, item_type.weight_g)
            )

            item_type_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Item type with this name already exists"
        )

    return {
        "id": item_type_id,
        "name": item_type.name,
        "weight_g": item_type.weight_g
    }


@router.patch("/{item_type_id}")
def update_item_type(item_type_id: int, update: ItemTypeUpdate):
    if update.name is None and "weight_g" not in update.model_fields_set:
        raise HTTPException(
            status_code=400,
            detail="Nothing to update: provide name and/or weight_g",
        )

    try:
        with get_db() as db:
            current = db.execute(
                "SELECT item_type_id, item_type_name, weight_g FROM item_type WHERE item_type_id = ?",
                (item_type_id,),
            ).fetchone()
            if current is None:
                raise HTTPException(status_code=404, detail="Item type not found")

            new_name = update.name if update.name is not None else current["item_type_name"]
            new_weight = (
                update.weight_g
                if "weight_g" in update.model_fields_set
                else current["weight_g"]
            )
            db.execute(
                "UPDATE item_type SET item_type_name = ?, weight_g = ? WHERE item_type_id = ?",
                (new_name, new_weight, item_type_id),
            )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Item type with this name already exists",
        )

    return get_item_type(item_type_id)


@router.delete("/{item_type_id}")
def delete_item_type(item_type_id: int):
    try:
        with get_db() as db:
            cursor = db.execute(
                """
                DELETE FROM item_type
                WHERE item_type_id = ?
                """,
                (item_type_id,)
            )

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Item type not found"
                )

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Item type is used by an item"
        )

    return {
        "message": "Item type deleted"
    }