package com.example.warehouse.data.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Содержимое ячейки (ответ GET /boxes/{id}/contents).
 */
public class BoxContents {
    public int box_id;
    public List<ItemRow> items = new ArrayList<>();
    public List<ChildBox> child_boxes = new ArrayList<>();

    public static class ItemRow {
        public int item_id;
        public int item_type_id;
        public String item_type_name;
        public Integer weight_g;
        public int quantity;
        public Integer total_weight_g;
    }

    public static class ChildBox {
        public int id;
        public String name;
        public int box_type_id;
        public String box_type_name;
    }
}
