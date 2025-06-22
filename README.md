# pyhold

PyPi: [Click Here](https://pypi.org/project/pyhold/)

**pyhold** is a lightweight, persistent data store built in pure Python with multiple data structure support. Designed for MVPs, CLI tools, and embedded apps that need quick and reliable state saving — no database required.

### ✅ Features
- **Dictionary-style access**: `store["token"] = "abc"`
- **Key-Value store**: Dedicated key-value operations with GUI
- **Linked List**: Persistent linked list with full list operations
- Auto-syncs to XML on change
- Supports `int`, `str`, `float`, `bool`, `dict`, `list`, `tuple`, `None`
- Fully human-readable and editable
- Zero external dependencies
- Built-in GUI for all data structures

### 📋 Requirements

**Python Version**: 3.7 or higher

**Built-in Dependencies** (included with Python):
- `tkinter` - For GUI functionality (included in most Python installations)
- `xml.etree.ElementTree` - For XML file operations
- `json` - For complex data type serialization
- `ast` - For literal evaluation

**Note**: The GUI features require `tkinter`, which is included in most Python installations but may need to be installed separately on some Linux distributions:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL/Fedora
sudo yum install tkinter
# or
sudo dnf install python3-tkinter

# macOS (usually included with Python)
# If missing: brew install python-tk
```

### Installation
```bash
pip install pyhold
```

## 🗂️ Key-Value Store

The key-value store provides dictionary-like functionality with persistent storage to XML files.

### Basic Usage
```python
from pyhold import pyhold

# Initialize in keyvalue mode
kv_store = pyhold("my_data.xml", mode="keyvalue", auto_sync=True, auto_reload=True)
```

### Core Functions

#### **Dictionary-style Operations**
```python
# Set values
kv_store["username"] = "john_doe"
kv_store["age"] = 25
kv_store["settings"] = {"theme": "dark", "notifications": True}

# Get values
print(kv_store["username"])  # "john_doe"
print(kv_store["age"])       # 25

# Check if key exists
if "username" in kv_store:
    print("User found!")

# Delete items
del kv_store["age"]
# or
kv_store.pop("age")  # Returns the value and removes it
```

#### **Utility Functions**
```python
# Get with default value
value = kv_store.get("missing_key", "default_value")

# Get all keys, values, or items
keys = kv_store.keys()      # ['username', 'settings']
values = kv_store.values()  # ['john_doe', {'theme': 'dark', 'notifications': True}]
items = kv_store.items()    # [('username', 'john_doe'), ('settings', {...})]

# Get length
print(len(kv_store))  # Number of key-value pairs

# Clear all data
kv_store.clear()

# Manual save/reload
kv_store.save_pyhold()   # Force save to XML
kv_store.load_pyhold()   # Force reload from XML
```

#### **Write Function**
```python
# Alternative way to add/update values
kv_store.write("api_key", "abc123")
kv_store.write("counter", 42)
```

#### **GUI Interface**
```python
# Open graphical interface for managing data
kv_store.show_gui()
```

### Complete Example
```python
from pyhold import pyhold

# Initialize store in keyvalue mode
config = pyhold("app_config.xml", mode="keyvalue")

# Store application settings
config["app_name"] = "MyApp"
config["version"] = "1.0.0"
config["debug_mode"] = True
config["database"] = {
    "host": "localhost",
    "port": 5432,
    "name": "myapp_db"
}
config["features"] = ["auth", "logging", "api"]

# Retrieve settings
print(f"App: {config['app_name']} v{config['version']}")
print(f"Debug: {config['debug_mode']}")
print(f"DB Host: {config['database']['host']}")

# Check if feature is enabled
if "auth" in config["features"]:
    print("Authentication is enabled")

# Update settings
config["version"] = "1.1.0"
config["debug_mode"] = False

# Open GUI to manage settings
config.show_gui()
```

## 🔗 Linked List

The linked list provides a persistent, index-based data structure with full list operations.

### Basic Usage
```python
from pyhold import pyhold

# Initialize in linkedlist mode
ll = pyhold("my_list.xml", mode="linkedlist", auto_sync=True, auto_reload=True)
```

### Core Functions

#### **List-style Operations**
```python
# Add items
ll.append("first item")
ll.append(42)
ll.append({"nested": "data"})

# Access by index
print(ll[0])  # "first item"
print(ll[1])  # 42

# Set items by index
ll[0] = "updated first item"

# Check if value exists
if "first item" in ll:
    print("Item found!")

# Get length
print(len(ll))  # Number of items
```

#### **Insertion and Removal**
```python
# Insert at specific index
ll.insert(1, "inserted item")  # Inserts at index 1

# Remove by value
ll.remove("inserted item")  # Removes first occurrence

# Remove by index
ll.pop(0)  # Removes and returns item at index 0
ll.pop()   # Removes and returns last item

# Delete by index
del ll[0]  # Removes item at index 0
```

#### **Search and Analysis**
```python
# Find index of value
try:
    index = ll.index("first item")
    print(f"Found at index: {index}")
except ValueError:
    print("Item not found")

# Count occurrences
count = ll.count("first item")  # Number of times item appears

# Check if lists are equal
other_list = pyhold("other.xml", mode="linkedlist")
other_list.append("first item")
print(ll == other_list)  # True if lists have same values
```

#### **List Manipulation**
```python
# Reverse the list
ll.reverse()

# Sort the list
ll.sort()           # Ascending order
ll.sort(reverse=True)  # Descending order

# Extend with another iterable
ll.extend(["item1", "item2", "item3"])

# Concatenate lists
list1 = pyhold("list1.xml", mode="linkedlist")
list2 = pyhold("list2.xml", mode="linkedlist")
combined = list1 + list2  # Creates new list

# Repeat list
repeated = ll * 3  # Creates list with ll repeated 3 times
```

#### **Utility Functions**
```python
# Clear all items
ll.clear()

# Manual save/reload
ll.save_pyhold()   # Force save to XML
ll.load_pyhold()   # Force reload from XML

# String representation
print(str(ll))  # Prints all values, one per line
```

#### **GUI Interface**
```python
# Open graphical interface for managing list
ll.show_gui()
```

### Complete Example
```python
from pyhold import pyhold

# Initialize list in linkedlist mode
tasks = pyhold("todo_list.xml", mode="linkedlist")

# Add tasks
tasks.append("Buy groceries")
tasks.append("Write documentation")
tasks.append("Review code")
tasks.append("Deploy application")

# Insert priority task
tasks.insert(0, "URGENT: Fix critical bug")

# Check current tasks
print(f"Total tasks: {len(tasks)}")
print(f"First task: {tasks[0]}")
print(f"Last task: {tasks[-1]}")

# Find specific task
try:
    index = tasks.index("Write documentation")
    print(f"Documentation task at index: {index}")
except ValueError:
    print("Task not found")

# Update task
tasks[1] = "Buy groceries and milk"

# Remove completed task
tasks.remove("Review code")

# Sort tasks alphabetically
tasks.sort()

# Reverse to see most recent first
tasks.reverse()

# Open GUI to manage tasks
tasks.show_gui()
```

## 📁 Dictionary Store

The dictionary store provides a simple key-value interface using the main `pyhold` class.

### Basic Usage
```python
from pyhold import pyhold

# Initialize in keyvalue mode (default)
store = pyhold("mydata.xml", mode="keyvalue", auto_sync=True, auto_reload=True)

# Use like a dictionary
store["username"] = "anjan"
store["token"] = "abc123"
print(store["username"])  # "anjan"

# Remove items
store.pop("username")
```

### Complete Example
```python
from pyhold import pyhold

# Initialize store
app_data = pyhold("app_data.xml", mode="keyvalue")

# Store user session data
app_data["user_id"] = 12345
app_data["session_token"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
app_data["preferences"] = {
    "theme": "dark",
    "language": "en",
    "notifications": True
}
app_data["last_login"] = "2024-01-15T10:30:00Z"

# Retrieve data
user_id = app_data.get("user_id")
session_token = app_data["session_token"]
theme = app_data["preferences"]["theme"]

# Update data
app_data["last_login"] = "2024-01-15T11:45:00Z"

# Check if key exists
if "session_token" in app_data:
    print("User is logged in")

# Remove sensitive data
app_data.pop("session_token")
```

## 🔧 Configuration Options

All classes support these initialization parameters:

- **`filename`** (str): XML file path for persistence (default: "pyhold.xml")
- **`mode`** (str): Data structure mode - "keyvalue" or "linkedlist" (default: "keyvalue")
- **`auto_sync`** (bool): Automatically save changes to file (default: True)
- **`auto_reload`** (bool): Automatically load from file on initialization (default: True)

## 🎨 GUI Features

Both key-value and linked list stores include a comprehensive GUI with:

- **Visual data management**: Add, edit, delete items
- **Search functionality**: Filter items by key/value
- **Type selection**: Choose data types (str, int, float, bool, list, dict, tuple)
- **File operations**: Manual save, reload, export to JSON
- **Real-time updates**: See changes immediately
- **Error handling**: User-friendly error messages

## 📋 Supported Data Types

- **Primitive types**: `int`, `str`, `float`, `bool`, `None`
- **Complex types**: `dict`, `list`, `tuple`
- **Automatic type detection** and preservation
- **Human-readable XML storage**

## 🚀 Use Cases

- **Configuration management**: App settings, user preferences
- **Session storage**: User data, authentication tokens
- **Data caching**: Temporary data persistence
- **CLI tools**: Command history, user settings
- **Prototyping**: Quick data storage without database setup
- **Embedded applications**: Lightweight data persistence

## 🔧 Troubleshooting

### GUI Not Working
If you encounter issues with the GUI:
1. **Linux**: Install tkinter: `sudo apt-get install python3-tk` (Ubuntu/Debian) or `sudo yum install tkinter` (CentOS/RHEL)
2. **macOS**: Usually included with Python. If missing: `brew install python-tk`
3. **Windows**: Usually included with Python installation

### File Permission Errors
- Ensure you have write permissions in the directory where you're creating XML files
- Check if the XML file is not locked by another process

### Data Type Issues
- Complex data types (dict, list, tuple) are automatically serialized to JSON
- None values are properly handled
- Boolean values are preserved correctly

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
```bash
git clone https://github.com/AnjanB3012/pyhold.git
cd pyhold
pip install -e .
```

### Running Tests
```python
# Basic functionality test
from pyhold import pyhold

# Test key-value store
kv = pyhold("test.xml", mode="keyvalue")
kv["test"] = "value"
assert kv["test"] == "value"

# Test linked list
ll = pyhold("test_list.xml", mode="linkedlist")
ll.append("item1")
assert ll[0] == "item1"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📝 Changelog

### Version 0.2.0
- Added comprehensive GUI for both key-value and linked list stores
- Improved error handling and data type support
- Enhanced documentation with examples
- Added search and filter functionality in GUI
- Export to JSON functionality

### Version 0.1.0
- Initial release with basic key-value and linked list functionality
- XML persistence support
- Basic dictionary-style operations