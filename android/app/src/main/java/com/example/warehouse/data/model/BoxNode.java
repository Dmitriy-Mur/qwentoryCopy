package com.example.warehouse.data.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Узел дерева складов (ответ GET /boxes/tree).
 */
public class BoxNode {
    public int id;
    public String name;
    public Integer box_type_id;
    public String box_type_name;
    public Integer parent_id;
    public List<BoxNode> children = new ArrayList<>();
}
