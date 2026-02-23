## 実行コマンド
uv run python .\server.py

uv run streamlit run app.py



## メモ

#### 概要

「**ユーザ名「Bret」のユーザの投稿を取得して**」をプロンプトで渡すと「`get_all_user_info`」「`get_all_posts_by_id`」の順でメソッドを実行して情報を取得する。<br>

LLMの思考プロセス
1. ユーザごとの投稿を取得するためにユーザIDが必要であることを「`get_all_posts_by_id`」の定義から理解する。
2. 「`get_all_user_info`」の定義から、全ユーザの情報が取得できることを理解して、メソッドを実行する。
3. 2の結果から「Bret」のユーザIDを取得して、「`get_all_posts_by_id`」のメソッドにより、投稿情報を取得する。


#### ログ

Cline wants to use a tool on the `my-custom-python-server` MCP server:
`get_all_user_info`

Cline wants to use a tool on the `my-custom-python-server` MCP server:
`get_all_posts_by_id`


<br>

```json
{
  "userId": "1"
}
```

**Task Completed**

```
ユーザ名「Bret」のユーザの投稿情報を取得しました。
ユーザID: 1 ユーザ名: Bret 名前: Leanne Graham

投稿情報:

1. sunt aut facere repellat provident occaecati excepturi optio reprehenderit
2. qui est esse
3. ea molestias quasi exercitationem repellat qui ipsa sit aut
4. eum et est occaecati
5. nesciunt quas odio
6. dolorem eum magni eos aperiam quia
7. magnam facilis autem
8. dolorem dolore est ipsam
9. nesciunt iure omnis dolorem tempora et accusantium
10. optio molestias id quia eum

全ての投稿はJSON形式で取得できました。投稿内容は上記の通りです。
```

