"""Автотест UI-фиксов: дерево, сортировка, скроллбары, тёмная тема.

Запускать из каталога desktop: xvfb-run -a python3 test_ui_fixes.py
"""
import sys
import tkinter as tk

import customtkinter as ctk

from database import init_db, get_session
from ui.main_window import MainWindow, natural_key


def collect_button_texts(widget, out):
    for child in widget.winfo_children():
        if isinstance(child, ctk.CTkButton):
            out.append(child.cget('text'))
        else:
            collect_button_texts(child, out)


def main():
    init_db()
    root = ctk.CTk()
    session = get_session()
    app = MainWindow(root, session)
    root.update_idletasks()
    root.update()

    failures = []

    def check(name, cond):
        print(('PASS' if cond else 'FAIL'), '-', name)
        if not cond:
            failures.append(name)

    # 1. Дерево показывает вложенные узлы
    texts = []
    collect_button_texts(app.tree, texts)
    joined = ' | '.join(texts)
    for expected in ['Основной склад', 'Стеллаж A', 'Полка 1', 'Ячейка A1-1',
                     'Склад ГСМ', 'Все товары', 'Без расположения']:
        check(f'derevo soderzhit: {expected}', expected in joined)
    check('derevo: kolichestvo uzlov >= 10', len([t for t in texts if '[' in t]) >= 10)

    # 2. Тёмная тема таблицы
    style = app.items_tree.cget('style')
    check('tablica: temnyi stil', style == 'Dark.Treeview')
    from ui.widgets import DARK_PANEL
    check('tablica: fon paneli temnyi', app.table.cget('fg_color') == DARK_PANEL)

    # 3. Сортировка по клику на шапку
    base_count = len(app.items_tree.get_children())
    check('tablica: est stroki', base_count > 0)
    first_before = app.items_tree.item(app.items_tree.get_children()[0], 'values')[0]
    app._sort_by_column('quantity')
    vals = [app.items_tree.item(iid, 'values')[1] for iid in app.items_tree.get_children()]
    nums = [int(v) for v in vals]
    check('sortirovka po kolichestvu po vozrastaniyu', nums == sorted(nums))
    check('zagolovok: strelka sortirovki', '▼' in app.items_tree.heading('quantity')['text'])
    app._sort_by_column('quantity')
    vals = [int(app.items_tree.item(iid, 'values')[1]) for iid in app.items_tree.get_children()]
    check('sortirovka po kolichestvu po ubyvaniyu', vals == sorted(vals, reverse=True))
    check('zagolovok: obratnaya strelka', '▲' in app.items_tree.heading('quantity')['text'])
    app._sort_by_column('type')
    types = [app.items_tree.item(iid, 'values')[0] for iid in app.items_tree.get_children()]
    check('sortirovka po tipu (A-Za-z/abvgd)', types == sorted(types, key=lambda s: s.lower()))
    app._sort_by_column('weight')
    w_first = app.items_tree.item(app.items_tree.get_children()[0], 'values')[2]
    print('   pervaya stroka posle sortirovki po vesu:', w_first)

    # 4. Разделители колонок существуют
    app.table._draw_column_separators()
    check('razdeliteli kolonok zadany', len(app.table._sep_canvas.find('all')) > 0)

    # 5. Скроллбар дерева скрыт, когда содержимое влезает
    app.tree._redraw_bar()
    needs = app.tree._needs_scroll
    drawn = int(app.tree._auto_bar.find('all').__len__())
    print('   derevo: needs_scroll =', needs, ', narisovano elementov =', drawn)

    # много узлов -> скроллбар нужен
    for i in range(60):
        b = ctk.CTkButton(app.tree, text=f'Dop uzol {i}')
        b.pack(fill='x')
    root.update_idletasks()
    root.update()
    app.tree._after_content_change()
    check('derevo: pri peremochenii soderzhimogo skrollbar nuzhen', app.tree._needs_scroll)
    check('derevo: polzunok narisovan', len(app.tree._auto_bar.find('all')) > 0)

    # 6. Вертикальный скроллбар таблицы скрыт при малом количестве строк
    app._sort_by_column('type')  # вернуть
    sel_box = -1
    app.selected_box_id = sel_box
    app._refresh_items()
    root.update_idletasks()
    root.update()
    is_mapped_v = app.table._vbar.winfo_ismapped()
    print('   tablica: strok =', len(app.items_tree.get_children()), ', vbar mapped =', bool(is_mapped_v))
    check('tablica: vbar skryt kogda vse vlezaet (malo strok)', is_mapped_v == 0)

    # 7. Выбор узла дерева фильтрует таблицу
    box_ids = [bid for bid in app.tree.nodes if isinstance(bid, int) and bid > 0]
    app.tree.select_node(box_ids[0])
    root.update()
    check('vybor uzla filtra tablicu', app.items_header.cget('text') != 'Все товары')

    session.close()
    root.destroy()

    print()
    if failures:
        print('FAILURES:', failures)
        sys.exit(1)
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
