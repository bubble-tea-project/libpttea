<h1 align="center">libpttea</h1>

<div align="center">

A Python library that encapsulates various PTT functions.


![GitHub last commit](https://img.shields.io/github/last-commit/bubble-tea-project/libpttea)
![GitHub License](https://img.shields.io/github/license/bubble-tea-project/libpttea)

</div>

## 📖 Description
libpttea 是一個 Python library，目的在封裝各種 PTT 功能操作，旨在輔助開發 [PTTea](https://github.com/bubble-tea-project/PTTea) APP 專案的 PTT 功能函式庫。

## ✨ Supported
- login
- logout
- system_info
- favorite_list
- post_list
- get_post
- in development...

## 🎨 Usage
```python
import libpttea

PTT_ACCOUNT = "PTT ID"
PTT_PASSWORD = "PTT 密碼"
lib_pttea = libpttea.login(PTT_ACCOUNT,PTT_PASSWORD)

system_info = lib_pttea.system_info()

lib_pttea.logout()

print(system_info)
# ['您現在位於 批踢踢實業坊 (140.112.172.11)', '系統負載: 輕輕鬆鬆', 
# '線上人數: 30602/175000', 'ClientCode: 02000023', '起始時間: 09/23/2024 17:49:24', 
# '編譯時間: Sun Jun  4 23:41:30 CST 2023', '編譯版本: https://github.com/ptt/pttbbs.git 0447b25c 8595c8b4 M']
```

## 📜 License
![GitHub License](https://img.shields.io/github/license/bubble-tea-project/libpttea)
