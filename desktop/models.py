"""Модели склада. Поля совпадают с REST API и прежним десктопным кодом."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class BoxType:
    box_type_id: int
    box_type_name: str

    @classmethod
    def from_api(cls, row: dict) -> "BoxType":
        return cls(box_type_id=row["id"], box_type_name=row["name"])


@dataclass
class Box:
    box_id: int
    box_name: str
    box_type_id: int
    parent_id: Optional[int] = None
    box_type_name: str = ""
    box_type: Optional[BoxType] = None
    parent: Optional["Box"] = None
    children: list = field(default_factory=list)

    @classmethod
    def from_api(cls, row: dict) -> "Box":
        box = cls(
            box_id=row["id"],
            box_name=row["name"],
            box_type_id=row["box_type_id"],
            parent_id=row.get("parent_id"),
            box_type_name=row.get("box_type_name") or "",
        )
        if box.box_type_name:
            box.box_type = BoxType(box.box_type_id, box.box_type_name)
        return box

    @property
    def full_path(self) -> str:
        parts = []
        current: Optional[Box] = self
        visited = set()
        while current is not None:
            if current.box_id in visited:
                break
            visited.add(current.box_id)
            parts.append(current.box_name)
            current = current.parent
        return " / ".join(reversed(parts))


@dataclass
class ItemType:
    item_type_id: int
    item_type_name: str
    weight_g: Optional[int] = None

    @classmethod
    def from_api(cls, row: dict) -> "ItemType":
        return cls(
            item_type_id=row["id"],
            item_type_name=row["name"],
            weight_g=row.get("weight_g"),
        )


@dataclass
class Item:
    item_id: int
    item_type_id: int
    box_id: Optional[int]
    quantity: int
    date: Optional[datetime] = None
    item_type: Optional[ItemType] = None
    box: Optional[Box] = None
    weight_g: Optional[int] = None
    box_name: Optional[str] = None
    api_total_weight_g: Optional[int] = None

    @classmethod
    def from_api(cls, row: dict) -> "Item":
        item = cls(
            item_id=row["id"],
            item_type_id=row["item_type_id"],
            box_id=row.get("box_id"),
            quantity=row["quantity"],
            weight_g=row.get("weight_g"),
            box_name=row.get("box_name"),
            api_total_weight_g=row.get("total_weight_g"),
        )
        item.item_type = ItemType(
            item_type_id=row["item_type_id"],
            item_type_name=row.get("item_type_name") or "—",
            weight_g=row.get("weight_g"),
        )
        if row.get("box_id") is not None:
            item.box = Box(
                box_id=row["box_id"],
                box_name=row.get("box_name") or "",
                box_type_id=0,
            )
        return item

    @property
    def total_weight_g(self) -> int:
        if self.api_total_weight_g is not None:
            return self.api_total_weight_g
        if self.item_type and self.item_type.weight_g:
            return self.item_type.weight_g * self.quantity
        return 0
