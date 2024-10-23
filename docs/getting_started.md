# Getting started

## 登入 PTT
輸入自己的帳號、密碼登入，取得一個 API object。

```python
# ...
lib_pttea = await libpttea.login(PTT_ACCOUNT,PTT_PASSWORD)
```

## 執行功能操作
執行自己想要的操作吧!

```python
# ...
system_info = await lib_pttea.get_system_info()
print(system_info)
# ['您現在位於 批踢踢實業坊 (140.112.172.11)', 
# '系統負載: 輕輕鬆鬆', 
# '線上人數: 27492/175000', 
# 'ClientCode: 02000023', 
# '起始時間: 10/20/2024 05:15:40', 
# '編譯時間: Sun Jun  4 23:41:30 CST 2023', 
# '編譯版本: https://github.com/ptt/pttbbs.git 0447b25c 8595c8b4 M']


latest_post_index = await lib_pttea.get_latest_post_index("C_Chat")
print(latest_post_index) # 352492

```

## 登出
使用後別忘了登出。

```python
# ...
await lib_pttea.logout()
```


## 完整範例
```python
async def main():

    lib_pttea = await libpttea.login(PTT_ACCOUNT,PTT_PASSWORD)

    system_info = await lib_pttea.get_system_info()
    print(system_info)
    
    latest_post_index = await lib_pttea.get_latest_post_index("C_Chat")
    print(latest_post_index)
    
    await lib_pttea.logout()

# run the coroutine 
asyncio.run(main())
```





