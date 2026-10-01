package com.example.warehouse.data.api;

import com.example.warehouse.data.model.BoxContents;
import com.example.warehouse.data.model.BoxNode;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Path;

/**
 * Сервер работает без аутентификации, поэтому запросы отправляются без токена.
 */
public interface ApiService {

    @GET("boxes/tree")
    Call<List<BoxNode>> getBoxTree();

    @GET("boxes/{boxId}/contents")
    Call<BoxContents> getBoxContents(@Path("boxId") int boxId);
}