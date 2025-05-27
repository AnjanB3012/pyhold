# datalink

**Datalink** is a lightweight, persistent, dictionary-like data store built in pure Python. Designed for MVPs, CLI tools, and embedded apps that need quick and reliable state saving — no database required.

### ✅ Features
- Dictionary-style access: `store["token"] = "abc"`
- Auto-syncs to XML on change
- Supports `int`, `str`, `float`, `bool`, `dict`, `list`, `tuple`, `None`
- Fully human-readable and editable
- Zero dependencies

### 🚀 Quick Start

```python
from datalink import Datalink

store = Datalink("mydata.xml", auto_sync=True)
store["username"] = "anjan"
print(store["username"])
store.pop("username")
