#!/usr/bin/env python3
"""
Скрипт для заполнения БД тестовыми данными.
Запуск: python seed_test_data.py
"""

import os
import random
import string
import sqlite3
from pathlib import Path

# Путь к БД (аналогично app/database.py)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("WAREHOUSE_DB", str(BASE_DIR / "data" / "warehouse.db")))
SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"


def init_db(conn):
    """Создаёт таблицы, если их нет."""
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='box_type'"
    )
    if cur.fetchone():
        print("ℹ️  Таблицы уже существуют, пропускаем инициализацию схемы.")
        return

    if SCHEMA_PATH.exists():
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        print("✅ Схема БД инициализирована.")
    else:
        print(f"⚠️  Файл схемы не найден: {SCHEMA_PATH}")
        raise FileNotFoundError(SCHEMA_PATH)


def clear_db(conn):
    """Очищает все таблицы."""
    for table in ["item", "item_type", "box", "box_type"]:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()
    print("🧹 Таблицы очищены.")


def random_code(letters=2, digits=2):
    """Генерирует код из букв и цифр, например 'AB12'."""
    return (
        ''.join(random.choices(string.ascii_uppercase, k=letters)) +
        ''.join(random.choices(string.digits, k=digits))
    )


def seed():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row

    init_db(conn)
    clear_db(conn)

    # 1. Типы коробок
    box_types = [
        ("Склад",),
        ("Стеллаж",),
        ("Полка",),
        ("Отсек",),
    ]
    conn.executemany("INSERT INTO box_type (box_type_name) VALUES (?)", box_types)
    conn.commit()

    # Получаем ID типов
    cur = conn.execute("SELECT box_type_id, box_type_name FROM box_type")
    type_map = {row["box_type_name"]: row["box_type_id"] for row in cur.fetchall()}

    # 2. Иерархия коробок
    num_warehouses = random.randint(1, 2)
    warehouses = []
    for i in range(num_warehouses):
        name = f"WH-{random_code()}"
        cur = conn.execute(
            "INSERT INTO box (box_name, box_type_id, parent_id) VALUES (?, ?, NULL)",
            (name, type_map["Склад"])
        )
        wh_id = cur.lastrowid
        warehouses.append(wh_id)

        # Стеллажи (2-3 на склад)
        for _ in range(random.randint(2, 3)):
            rack_name = f"R-{random_code()}"
            cur = conn.execute(
                "INSERT INTO box (box_name, box_type_id, parent_id) VALUES (?, ?, ?)",
                (rack_name, type_map["Стеллаж"], wh_id)
            )
            rack_id = cur.lastrowid

            # Полки (2-3 на стеллаж)
            for _ in range(random.randint(2, 3)):
                shelf_name = f"S-{random_code()}"
                cur = conn.execute(
                    "INSERT INTO box (box_name, box_type_id, parent_id) VALUES (?, ?, ?)",
                    (shelf_name, type_map["Полка"], rack_id)
                )
                shelf_id = cur.lastrowid

                # Отсеки (1-3 на полку)
                for _ in range(random.randint(1, 3)):
                    cell_name = f"C-{random_code()}"
                    conn.execute(
                        "INSERT INTO box (box_name, box_type_id, parent_id) VALUES (?, ?, ?)",
                        (cell_name, type_map["Отсек"], shelf_id)
                    )
    conn.commit()
    print(f"✅ Создано {num_warehouses} складов с иерархией контейнеров.")

    # 3. Типы предметов (стройматериалы)
    materials = [
        ("Цемент М500", 50000),
        ("Кирпич красный", 3000),
        ("Кирпич силикатный", 4000),
        ("Песок строительный", 25000),
        ("Щебень гранитный", 20000),
        ("Арматура 12 мм", 1000),
        ("Арматура 16 мм", 1500),
        ("Проволока вязальная", 500),
        ("Доска обрезная 25 мм", 5000),
        ("Доска обрезная 50 мм", 8000),
        ("Брус 100×100", 10000),
        ("Фанера 12 мм", 6000),
        ("Гипсокартон", 8000),
        ("Профиль металлический", 2000),
        ("Утеплитель минеральная вата", 3000),
        ("Пенополистирол", 1000),
        ("Пленка парoизоляционная", 2000),
        ("Руberoid", 5000),
        ("Штукатурка гипсовая", 30000),
        ("Шпаклевка финишная", 25000),
        ("Краска фасадная", 15000),
        ("Эмаль ПФ-115", 10000),
        ("Грунтовка глубокого проникновения", 5000),
        ("Плитка керамическая", 2000),
        ("Клей плиточный", 25000),
        ("Саморезы кровельные", 1000),
        ("Дюбели", 500),
        ("Кабель ВВГ 3×2.5", 200),
        ("Гофра ПВХ", 100),
        ("Труба ПНД 32 мм", 300),
        ("Фитинги полипропиленовые", 100),
    ]
    conn.executemany(
        "INSERT INTO item_type (item_type_name, weight_g) VALUES (?, ?)",
        materials
    )
    conn.commit()
    print(f"✅ Добавлено {len(materials)} типов предметов.")

    # Получаем все ID типов предметов
    cur = conn.execute("SELECT item_type_id FROM item_type")
    item_type_ids = [row["item_type_id"] for row in cur.fetchall()]

    # 4. Предметы в коробках
    cur = conn.execute(
        "SELECT box_id FROM box WHERE box_type_id = ?",
        (type_map["Отсек"],)
    )
    cell_ids = [row["box_id"] for row in cur.fetchall()]

    # Предметы в отсеках
    for cell_id in cell_ids:
        num_types = random.randint(1, 4)
        selected_types = random.sample(item_type_ids, min(num_types, len(item_type_ids)))
        for item_type_id in selected_types:
            quantity = random.randint(1, 100)
            conn.execute(
                "INSERT INTO item (item_type_id, box_id, quantity) VALUES (?, ?, ?)",
                (item_type_id, cell_id, quantity)
            )

    # Предметы на складах (без отсека)
    for wh_id in warehouses:
        num_types = random.randint(2, 5)
        selected_types = random.sample(item_type_ids, min(num_types, len(item_type_ids)))
        for item_type_id in selected_types:
            quantity = random.randint(5, 200)
            conn.execute(
                "INSERT INTO item (item_type_id, box_id, quantity) VALUES (?, ?, ?)",
                (item_type_id, wh_id, quantity)
            )

    # Предметы вне коробок (box_id = NULL)
    num_unboxed = random.randint(3, 8)
    selected_types = random.sample(item_type_ids, min(num_unboxed, len(item_type_ids)))
    for item_type_id in selected_types:
        quantity = random.randint(1, 50)
        conn.execute(
            "INSERT INTO item (item_type_id, box_id, quantity) VALUES (?, NULL, ?)",
            (item_type_id, quantity)
        )

    conn.commit()
    conn.close()
    print("🎉 База данных успешно заполнена тестовыми данными.")


if __name__ == "__main__":
    seed()