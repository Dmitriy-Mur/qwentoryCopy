"""CRUD через REST API. Сигнатуры сохранены, чтобы UI не переписывать с нуля."""
from __future__ import annotations

from typing import List, Optional

from api_client import ApiClient, ApiError
from models import Box, BoxType, Item, ItemType


def _link_boxes(boxes: List[Box]) -> List[Box]:
    by_id = {box.box_id: box for box in boxes}
    for box in boxes:
        if box.parent_id is not None:
            box.parent = by_id.get(box.parent_id)
    return boxes


def get_all_box_types(client: ApiClient) -> List[BoxType]:
    return [BoxType.from_api(row) for row in client.get("/box-types")]


def add_box_type(client: ApiClient, name: str) -> BoxType:
    return BoxType.from_api(client.post("/box-types", {"name": name}))


def get_all_boxes(client: ApiClient) -> List[Box]:
    return _link_boxes([Box.from_api(row) for row in client.get("/boxes")])


def get_root_boxes(client: ApiClient) -> List[Box]:
    return [box for box in get_all_boxes(client) if box.parent_id is None]


def get_child_boxes(client: ApiClient, parent_id: Optional[int]) -> List[Box]:
    if parent_id is None:
        return get_root_boxes(client)
    return [box for box in get_all_boxes(client) if box.parent_id == parent_id]


def get_box_by_id(client: ApiClient, box_id: int) -> Optional[Box]:
    try:
        box = Box.from_api(client.get(f"/boxes/{box_id}"))
    except ApiError as error:
        if error.status == 404:
            return None
        raise
    by_id = {b.box_id: b for b in get_all_boxes(client)}
    current = by_id.get(box.box_id, box)
    return current


def add_box(client: ApiClient, name: str, box_type_id: int, parent_id: Optional[int]) -> Box:
    return Box.from_api(client.post("/boxes", {
        "name": name,
        "box_type_id": box_type_id,
        "parent_id": parent_id,
    }))


def update_box(
    client: ApiClient,
    box_id: int,
    name: str,
    box_type_id: int,
    parent_id: Optional[int],
) -> None:
    client.patch(f"/boxes/{box_id}", {"name": name, "box_type_id": box_type_id})
    client.post(f"/boxes/{box_id}/move", {"parent_id": parent_id})


def delete_box(client: ApiClient, box_id: int) -> int:
    result = client.delete(f"/boxes/{box_id}") or {}
    return int(result.get("unboxed") or 0)


def get_box_full_path(client: ApiClient, box_id: Optional[int]) -> str:
    if box_id is None:
        return "Без расположения"
    box = get_box_by_id(client, box_id)
    if not box:
        return "Без расположения"
    return box.full_path


def get_all_item_types(client: ApiClient) -> List[ItemType]:
    return [ItemType.from_api(row) for row in client.get("/item-types")]


def add_item_type(client: ApiClient, name: str, weight_g: Optional[int]) -> ItemType:
    return ItemType.from_api(client.post("/item-types", {"name": name, "weight_g": weight_g}))


def update_item_type(client: ApiClient, item_type_id: int, name: str, weight_g: Optional[int]) -> None:
    client.patch(f"/item-types/{item_type_id}", {"name": name, "weight_g": weight_g})


def get_item_by_id(client: ApiClient, item_id: int) -> Optional[Item]:
    try:
        item = Item.from_api(client.get(f"/items/{item_id}"))
    except ApiError as error:
        if error.status == 404:
            return None
        raise
    _attach_boxes(client, [item])
    return item


def get_all_items(client: ApiClient) -> List[Item]:
    items = [Item.from_api(row) for row in client.get("/items")]
    _attach_boxes(client, items)
    return items


def get_items_by_box(client: ApiClient, box_id: int, include_children: bool = True) -> List[Item]:
    items = [
        Item.from_api(row)
        for row in client.get("/items", {"box_id": box_id, "include_children": str(include_children).lower()})
    ]
    _attach_boxes(client, items)
    return items


def get_items_without_box(client: ApiClient) -> List[Item]:
    items = [Item.from_api(row) for row in client.get("/items", {"unboxed": "true"})]
    return items


def add_item(client: ApiClient, item_type_id: int, box_id: Optional[int], quantity: int) -> Item:
    return Item.from_api(client.post("/items", {
        "item_type_id": item_type_id,
        "box_id": box_id,
        "quantity": quantity,
    }))


def update_item(
    client: ApiClient,
    item_id: int,
    item_type_id: int,
    box_id: Optional[int],
    quantity: int,
) -> None:
    client.patch(f"/items/{item_id}", {
        "item_type_id": item_type_id,
        "box_id": box_id,
        "quantity": quantity,
    })


def delete_item(client: ApiClient, item_id: int) -> None:
    client.delete(f"/items/{item_id}")


def search_items(client: ApiClient, query: str) -> List[Item]:
    needle = query.lower().strip()
    result = []
    for item in get_all_items(client):
        type_name = (item.item_type.item_type_name if item.item_type else "").lower()
        location = get_box_full_path(client, item.box_id).lower()
        if needle in type_name or needle in location:
            result.append(item)
    return result


def _attach_boxes(client: ApiClient, items: List[Item]) -> None:
    boxes = {box.box_id: box for box in get_all_boxes(client)}
    for item in items:
        if item.box_id is not None and item.box_id in boxes:
            item.box = boxes[item.box_id]
