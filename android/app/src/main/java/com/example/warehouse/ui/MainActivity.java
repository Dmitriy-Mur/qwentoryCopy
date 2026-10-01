package com.example.warehouse.ui;

import android.os.Bundle;
import android.view.View;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.warehouse.adapter.WarehouseAdapter;
import com.example.warehouse.data.api.ApiClient;
import com.example.warehouse.data.model.BoxContents;
import com.example.warehouse.data.model.BoxNode;
import com.example.warehouse.databinding.ActivityMainBinding;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Главный экран приложения. Регистрация и аутентификация не используются —
 * приложение сразу открывает структуру склада, сервер доступен без токена.
 */
public class MainActivity extends AppCompatActivity {

    private ActivityMainBinding binding;
    private WarehouseAdapter adapter;

    /** Корень дерева складов (кэш ответа /boxes/tree). */
    private List<BoxNode> treeRoots;

    /** Путь от корня к текущей ячейке (включая саму текущую). */
    private final Deque<BoxNode> path = new ArrayDeque<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        adapter = new WarehouseAdapter(this);
        binding.list.setAdapter(adapter);

        binding.btnRefresh.setOnClickListener(v -> loadTree());
        binding.btnUp.setOnClickListener(v -> goUp());
        binding.swipeRefresh.setOnRefreshListener(this::loadTree);

        binding.list.setOnItemClickListener((parent, view, position, id) -> {
            WarehouseAdapter.Row row = adapter.getItem(position);
            if (row != null && row.isBox) {
                openBox(row.box);
            }
        });

        loadTree();
    }

    private void loadTree() {
        setLoading(true);

        ApiClient.api().getBoxTree().enqueue(new Callback<List<BoxNode>>() {
            @Override
            public void onResponse(Call<List<BoxNode>> call, Response<List<BoxNode>> response) {
                setLoading(false);
                binding.swipeRefresh.setRefreshing(false);

                if (response.isSuccessful() && response.body() != null) {
                    treeRoots = response.body();
                    path.clear();
                    renderLevel();
                } else {
                    toast("Ошибка загрузки дерева: " + response.code());
                }
            }

            @Override
            public void onFailure(Call<List<BoxNode>> call, Throwable t) {
                setLoading(false);
                binding.swipeRefresh.setRefreshing(false);
                toast("Сеть недоступна: " + t.getMessage());
            }
        });
    }

    private void openBox(BoxNode box) {
        path.addLast(box);
        loadContents(box);
    }

    private void goUp() {
        if (!path.isEmpty()) {
            path.removeLast();
            renderLevel();
        }
    }

    /**
     * Верхний уровень: показываем корневые ячейки.
     */
    private void renderLevel() {
        updatePathLabel();

        if (path.isEmpty()) {
            List<WarehouseAdapter.Row> rows = new ArrayList<>();
            if (treeRoots != null) {
                for (BoxNode node : treeRoots) {
                    rows.add(WarehouseAdapter.Row.ofBox(node));
                }
            }
            adapter.setRows(rows);
            return;
        }

        loadContents(path.peekLast());
    }

    /**
     * Содержимое конкретной ячейки: вложенные коробки + товары.
     */
    private void loadContents(BoxNode current) {
        updatePathLabel();
        setLoading(true);

        ApiClient.api().getBoxContents(current.id)
                .enqueue(new Callback<BoxContents>() {
                    @Override
                    public void onResponse(Call<BoxContents> call,
                                           Response<BoxContents> response) {
                        setLoading(false);
                        binding.swipeRefresh.setRefreshing(false);

                        if (response.isSuccessful() && response.body() != null) {
                            BoxContents contents = response.body();
                            List<WarehouseAdapter.Row> rows = new ArrayList<>();

                            for (BoxContents.ChildBox child : contents.child_boxes) {
                                rows.add(WarehouseAdapter.Row.ofBox(toNode(child)));
                            }
                            for (BoxContents.ItemRow item : contents.items) {
                                rows.add(WarehouseAdapter.Row.ofItem(item));
                            }
                            adapter.setRows(rows);
                        } else {
                            toast("Ошибка загрузки содержимого: " + response.code());
                        }
                    }

                    @Override
                    public void onFailure(Call<BoxContents> call, Throwable t) {
                        setLoading(false);
                        binding.swipeRefresh.setRefreshing(false);
                        toast("Сеть недоступна: " + t.getMessage());
                    }
                });
    }

    private static BoxNode toNode(BoxContents.ChildBox child) {
        BoxNode node = new BoxNode();
        node.id = child.id;
        node.name = child.name;
        node.box_type_id = child.box_type_id;
        node.box_type_name = child.box_type_name;
        return node;
    }

    private void updatePathLabel() {
        binding.btnUp.setEnabled(!path.isEmpty());

        StringBuilder sb = new StringBuilder("Склад");
        for (BoxNode node : path) {
            sb.append(" / ").append(node.name);
        }
        binding.tvPath.setText(sb);
    }

    private void setLoading(boolean loading) {
        binding.progress.setVisibility(loading ? View.VISIBLE : View.GONE);
    }

    private void toast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }
}
