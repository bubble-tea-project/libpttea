# 取得文章資料

```{eval-rst}
.. module:: libpttea.api

```


```{eval-rst}
.. automethod:: API.get_post

```

## 範例
`get_post()` 回傳一個 Asynchronous Generator，每次回傳文章的"一頁"資料，直到全部載入為止。

我們可以用 `async for` 取得資料。

```python
# ...
post_content = []
post_reply = []

post_data = await lib_pttea.get_post( "C_Chat" , 352036 )
async for page_data in post_data:
    content , reply = page_data

    post_content.extend(content)
    post_reply.extend(reply)

```




