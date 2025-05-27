import xml.etree.ElementTree as ET
import os
import json
import tkinter as tk

class pyhold:
    def __init__(self, filename="pyhold.xml", mode="keyvalue", auto_sync=True, auto_reload=True):
        self.filename = filename
        self.mode = mode
        self.auto_sync = auto_sync
        self.auto_reload = auto_reload
        if self.auto_reload:
            if not os.path.exists(self.filename):
                if self.mode == "keyvalue":
                    self.volatileMem = []
            else:
                self.volatileMem = []
                self.load_pyhold()
        else:
            self.volatileMem = []

    def write(self, key=None, value=None):
        if self.mode == "keyvalue":
            if key is None:
                raise ValueError("Key must be provided in keyvalue mode.")
            for item in self.volatileMem:
                if item.key == key:
                    item.value = value
                    item.dtype = self.__keyvalNode(key, value).dtype
                    if self.auto_sync:
                        self.save_pyhold()
                    return
            tempNode = self.__keyvalNode(key, value)
            self.volatileMem.append(tempNode)
            if self.auto_sync:
                self.save_pyhold()

    def __getitem__(self, key):
        if self.mode == "keyvalue":
            for item in self.volatileMem:
                if item.key == key:
                    return item.value
            raise KeyError(f"Key '{key}' not found.")
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def __len__(self):
        if self.mode == "keyvalue":
            return len(self.volatileMem)
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def __iter__(self):
        if self.mode == "keyvalue":
            return iter(self.volatileMem)
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def __contains__(self, key):
        if self.mode == "keyvalue":
            return any(item.key == key for item in self.volatileMem)
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def __setitem__(self, key, value):
        if self.mode == "keyvalue":
            for item in self.volatileMem:
                if item.key == key:
                    item.value = value
                    if self.auto_sync:
                        self.save_pyhold()
                    return
            self.write(key, value)
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")
    
    def __delitem__(self, key):
        if self.mode == "keyvalue":
            for i, item in enumerate(self.volatileMem):
                if item.key == key:
                    del self.volatileMem[i]
                    if self.auto_sync:
                        self.save_pyhold()
                    return
            raise KeyError(f"Key '{key}' not found.")
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def pop(self, key):
        if self.mode == "keyvalue":
            for i, item in enumerate(self.volatileMem):
                if item.key == key:
                    value = item.value
                    del self.volatileMem[i]
                    if self.auto_sync:
                        self.save_pyhold()
                    return value
            raise KeyError(f"Key '{key}' not found.")
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def save_pyhold(self):
        if self.mode == "keyvalue":
            root = ET.Element("pyhold")
            for item in self.volatileMem:
                key_val = ET.SubElement(root, "keyval")

                key_elem = ET.SubElement(key_val, "key")
                key_elem.text = item.key

                value_elem = ET.SubElement(key_val, "value")
                value_elem.set("dtype", item.dtype)

                if item.dtype in ["dict", "list", "tuple"]:
                    value_elem.text = json.dumps(item.value)
                elif item.value is None:
                    value_elem.text = "None"
                else:
                    value_elem.text = str(item.value)

            tree = ET.ElementTree(root)
            tree.write(self.filename, encoding='utf-8', xml_declaration=True)
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def load_pyhold(self):
        if not os.path.exists(self.filename):
            return

        self.volatileMem.clear()
        tree = ET.parse(self.filename)
        root = tree.getroot()

        for keyval in root.findall("keyval"):
            key = keyval.find("key").text
            value_elem = keyval.find("value")
            dtype = value_elem.attrib.get("dtype", "str")
            value_str = value_elem.text

            if dtype == "int":
                value = int(value_str)
            elif dtype == "float":
                value = float(value_str)
            elif dtype == "bool":
                value = value_str == "True"
            elif dtype == "dict":
                value = json.loads(value_str)
            elif dtype == "list":
                value = json.loads(value_str)
            elif dtype == "tuple":
                value = tuple(json.loads(value_str))
            elif dtype == "NoneType" or value_str == "None":
                value = None
            else:
                value = value_str

            self.volatileMem.append(self.__keyvalNode(key, value))

    def showGUI(self):
        if self.mode != "keyvalue":
            raise NotImplementedError("Only keyvalue mode is implemented for GUI.")

        root = tk.Tk()
        root.title("pyhold Key-Value Store")

        frame = tk.Frame(root)
        frame.pack(padx=10, pady=10)

        listbox = tk.Listbox(frame, width=50, height=20)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)

        for item in self.volatileMem:
            listbox.insert(tk.END, f"{item.key}: {item.value} ({item.dtype})")

        root.mainloop()

    class __keyvalNode:
        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.dtype = type(value).__name__