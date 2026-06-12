# math64

一些数论与多进制有理数相关的小脚本整理仓库。

当前主线保留的是 `g进数` 实现：它支持任意合法进制下的有理数精确表示、运算、小数循环节表示，以及广义 g-adic 展开与有理数重构。

## 目录

- `src/math64/g_adic.py`: 多进制有理数与 g-adic 实现
- `tests/test_g_adic.py`: pytest 测试
- `docs/g_adic_api.md`: API 说明文档
- `archive/`: 旧版 p-adic 实现与历史测试归档

## 快速运行

```powershell
$env:PYTHONPATH = "src"
python -m pytest
```

## 示例

```python
from math64 import g进数

x = g进数(7, 30)
print(x.padic表示())  # (6).9

y = g进数.有理数重构("(6).9")
print(y == x)  # True
```
