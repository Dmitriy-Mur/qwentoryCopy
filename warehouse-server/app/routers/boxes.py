import sqlite3

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database import get_db


router = APIRouter(
    prefix="/boxes",
    tags=["Boxes"]
)


class BoxCreate(BaseModel):
    name: str
    box_type_id: int
    parent_id: int | None = None


@router.get("")
def get_boxes():
    with get_db() as db:
        rows = db.execute(
            """
            SELECT
                b.box_id,
                b.box_name,
                b.box_type_id,
                bt.box_type_name,
                b.parent_id
            FROM box b
            JOIN box_type bt ON bt.box_type_id = b.box_type_id
            ORDER BY b.box_id
            """
        ).fetchall()

    return [
        {
            "id": row["box_id"],
            "name": row["box_name"],
            "box_type_id": row["box_type_id"],
            "box_type_name": row["box_type_name"],
            "parent_id": row["parent_id"]
        }
        for row in rows
    ]


@router.get("/{box_id}")
def get_box(box_id: int):
    with get_db() as db:
        row = db.execute(
            """
            SELECT
                b.box_id,
                b.box_name,
                b.box_type_id,
                bt.box_type_name,
                b.parent_id
            FROM box b
            JOIN box_type bt ON bt.box_type_id = b.box_type_id
            WHERE b.box_id = ?
            """,
            (box_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Box not found"
        )

    return {
        "id": row["box_id"],
        "name": row["box_name"],
        "box_type_id": row["box_type_id"],
        "box_type_name": row["box_type_name"],
        "parent_id": row["parent_id"]
    }


@router.post("")
def create_box(box: BoxCreate):
    try:
        with get_db() as db:

            # Проверяем существование типа коробки
            type_exists = db.execute(
                """
                SELECT 1
                FROM box_type
                WHERE box_type_id = ?
                """,
                (box.box_type_id,)
            ).fetchone()

            if type_exists is None:
                raise HTTPException(
                    status_code=404,
                    detail="Box type not found"
                )

            # Если указана родительская коробка,
            # проверяем её существование
            if box.parent_id is not None:
                parent_exists = db.execute(
                    """
                    SELECT 1
                    FROM box
                    WHERE box_id = ?
                    """,
                    (box.parent_id,)
                ).fetchone()

                if parent_exists is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Parent box not found"
                    )

            cursor = db.execute(
                """
                INSERT INTO box (
                    box_name,
                    box_type_id,
                    parent_id
                )
                VALUES (?, ?, ?)
                """,
                (
                    box.name,
                    box.box_type_id,
                    box.parent_id
                )
            )

            box_id = cursor.lastrowid

    except sqlite3.IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error)
        )

    return {
        "id": box_id,
        "name": box.name,
        "box_type_id": box.box_type_id,
        "parent_id": box.parent_id
    }


@router.delete("/{box_id}")
def delete_box(box_id: int):
    with get_db() as db:
        cursor = db.execute(
            """
            DELETE FROM box
            WHERE box_id = ?
            """,
            (box_id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Box not found"
            )

    return {
        "message": "Box deleted"
    }