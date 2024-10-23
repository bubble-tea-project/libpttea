# 安裝 LibPttea

## Python 版本
建議使用最新的 Python 版本，最低要求 [Python ≥ 3.10](https://www.python.org/)。

## Dependency
LibPttea 目前依賴於以下套件，在安裝過程中將會自動安裝，細節可參考 [pyproject.toml](https://github.com/bubble-tea-project/libpttea/blob/main/pyproject.toml)。
- [AnsiParser](https://github.com/bubble-tea-project/ansiparser) is a convenient library for converting ANSI escape sequences into text or HTML.
- [websockets](https://github.com/python-websockets/websockets) is a library for building WebSocket servers and clients in Python with a focus on correctness, simplicity, robustness, and performance.

## 安裝
你可以使用以下方式安裝 LibPttea。
> 建議使用 Python 套件管理器，來管理套件及虛擬環境。

### [Poetry](https://github.com/python-poetry/poetry) (推薦)
```bash
poetry add libpttea
```

### Pip
```bash
pip install libpttea
```


