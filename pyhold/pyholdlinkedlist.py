import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ast
import xml.etree.ElementTree as ET

class LoadError(Exception):
    pass

class llNode:
    def __init__(self, value):
        self.value = value
        self.dtype = type(value).__name__
        self.next = None

    def __str__(self):
        return f"Value: {self.value}, Dtype: {self.dtype}"

class pyholdlinkedlist:
    def __init__(self, filename="pyhold.xml", auto_sync=True, auto_reload=True):
        self.filename = filename
        self.auto_sync = auto_sync
        self.auto_reload = auto_reload
        self.volatileMem = None
        if self.auto_reload:
            self.load_pyhold()

    def __str__(self):
        tempNode = self.volatileMem
        result = ""
        while tempNode is not None:
            result += str(tempNode.value) + "\n"
            tempNode = tempNode.next
        return result
    
    def save_pyhold(self):
        root = ET.Element("pyhold")
        tempHead = self.volatileMem
        tempIndex = 0
        while tempHead is not None:
            tempNode = ET.SubElement(root, "node")
            tempNode.set("index", str(tempIndex))
            tempNode.set("dtype", tempHead.dtype)
            
            # Handle boolean values specially
            if tempHead.dtype == "bool":
                tempNode.text = str(tempHead.value).lower()
            elif tempHead.dtype == "dict":
                tempNode.text = json.dumps(tempHead.value)
            elif tempHead.dtype == "tuple":
                tempNode.text = str(tempHead.value)
            elif tempHead.dtype == "list":
                tempNode.text = json.dumps(tempHead.value)
            else:
                tempNode.text = str(tempHead.value)
            
            tempHead = tempHead.next
            tempIndex += 1
        tree = ET.ElementTree(root)
        tree.write(self.filename, encoding='utf-8', xml_declaration=True)

    def load_pyhold(self):
        if not os.path.exists(self.filename):
            return
        
        # Check if file is empty
        if os.path.getsize(self.filename) == 0:
            return
            
        try:
            tree = ET.parse(self.filename)
            root = tree.getroot()
        except ET.ParseError:
            # Handle malformed XML
            return
            
        self.volatileMem = None
        tempVolatileMem = {}
        numOfNodes = len(root.findall("node"))
        for node in root.findall("node"):
            index = int(node.get("index"))
            dtype = node.get("dtype")
            value = node.text
            
            if dtype == "NoneType" or value == "None":
                value = None
            elif dtype == "bool":
                value = value.lower() == "true"
            elif dtype == "dict":
                value = json.loads(value)
            elif dtype == "tuple":
                value = ast.literal_eval(value)
            elif dtype == "list":
                value = ast.literal_eval(value)
            elif dtype == "str":
                value = str(value)
            elif dtype == "int":
                value = int(value)
            elif dtype == "float":
                value = float(value)
            else:
                raise LoadError(f"Unsupported dtype: {dtype}")
            
            tempVolatileMem[index] = value
        for i in range(numOfNodes):
            if i in tempVolatileMem:
                if self.volatileMem is None:
                    self.volatileMem = llNode(tempVolatileMem[i])
                else:
                    tempNode = self.volatileMem
                    while tempNode.next is not None:
                        tempNode = tempNode.next
                    tempNode.next = llNode(tempVolatileMem[i])

    def __getitem__(self, index):
        # Check for negative indices
        if index < 0:
            raise IndexError(f"Index {index} is out of range")
            
        tempNode = self.volatileMem
        for i in range(index):
            if tempNode is None:
                raise IndexError(f"Index {index} is out of range")
            tempNode = tempNode.next
        if tempNode is None:
            raise IndexError(f"Index {index} is out of range")
        return tempNode.value
    
    def __setitem__(self, index, value):
        if self.volatileMem is None:
            raise IndexError("set item on empty list")
        if index < 0:
            raise IndexError(f"Index {index} is out of range")
        tempNode = self.volatileMem
        for i in range(index):
            tempNode = tempNode.next
            if tempNode is None:
                raise IndexError(f"Index {index} is out of range")
        tempNode.value = value
        if self.auto_sync:
            self.save_pyhold()

    def __delitem__(self, index):
        if self.volatileMem is None:
            raise IndexError("delete from empty list")
        if index == 0:
            self.volatileMem = self.volatileMem.next
        else:
            prevNode = self.volatileMem
            for i in range(index - 1):
                if prevNode is None or prevNode.next is None:
                    raise IndexError(f"Index {index} is out of range")
                prevNode = prevNode.next
            if prevNode.next is None:
                raise IndexError(f"Index {index} is out of range")
            prevNode.next = prevNode.next.next
        if self.auto_sync:
            self.save_pyhold()

    def __len__(self):
        tempNode = self.volatileMem
        length = 0
        while tempNode is not None:
            length += 1
            tempNode = tempNode.next
        return length
    
    def __iter__(self):
        tempNode = self.volatileMem
        while tempNode is not None:
            yield tempNode.value
            tempNode = tempNode.next

    def __contains__(self, value):
        tempNode = self.volatileMem
        while tempNode is not None:
            if tempNode.value == value:
                return True
            tempNode = tempNode.next
        return False
    
    def append(self, value):
        if self.volatileMem is None:
            self.volatileMem = llNode(value)
        else:
            tempNode = self.volatileMem
            while tempNode.next is not None:
                tempNode = tempNode.next
            tempNode.next = llNode(value)
        if self.auto_sync:
            self.save_pyhold()

    def pop(self, index=None):
        if self.volatileMem is None:
            raise IndexError("pop from empty list")
        if index is None:
            index = len(self) - 1
        if index == 0:
            value = self.volatileMem.value
            self.volatileMem = self.volatileMem.next
        else:
            prevNode = self.volatileMem
            for i in range(index - 1):
                if prevNode is None or prevNode.next is None:
                    raise IndexError(f"Index {index} is out of range")
                prevNode = prevNode.next
            if prevNode.next is None:
                raise IndexError(f"Index {index} is out of range")
            value = prevNode.next.value
            prevNode.next = prevNode.next.next
        if self.auto_sync:
            self.save_pyhold()
        return value

    def clear(self):
        self.volatileMem = None
        if self.auto_sync:
            self.save_pyhold()
    
    def insert(self, index, value):
        if index == 0:
            newNode = llNode(value)
            newNode.next = self.volatileMem
            self.volatileMem = newNode
        else:
            prevNode = self.volatileMem
            for i in range(index - 1):
                if prevNode is None:
                    raise IndexError(f"Index {index} is out of range")
                prevNode = prevNode.next
            if prevNode is None:
                raise IndexError(f"Index {index} is out of range")
            newNode = llNode(value)
            newNode.next = prevNode.next
            prevNode.next = newNode
        if self.auto_sync:
            self.save_pyhold()

    def remove(self, value):
        tempNode = self.volatileMem
        prevNode = None
        while tempNode is not None:
            if tempNode.value == value:
                if prevNode is None:
                    self.volatileMem = tempNode.next
                else:
                    prevNode.next = tempNode.next
                if self.auto_sync:
                    self.save_pyhold()
                return
            prevNode = tempNode
            tempNode = tempNode.next
        raise ValueError(f"Value {value} not found in linked list")
    
    def index(self, value):
        tempNode = self.volatileMem
        index = 0
        while tempNode is not None:
            if tempNode.value == value:
                return index
            index += 1
            tempNode = tempNode.next    
        raise ValueError(f"Value {value} not found in linked list")
    
    def count(self, value):
        tempNode = self.volatileMem
        count = 0
        while tempNode is not None:
            if tempNode.value == value:
                count += 1
            tempNode = tempNode.next
        return count
    
    def reverse(self):
        prevNode = None
        currentNode = self.volatileMem
        while currentNode is not None:
            nextNode = currentNode.next
            currentNode.next = prevNode
            prevNode = currentNode
            currentNode = nextNode
        self.volatileMem = prevNode
        if self.auto_sync:
            self.save_pyhold()
    
    def extend(self, iterable):
        for item in iterable:
            self.append(item)
        if self.auto_sync:
            self.save_pyhold()
    
    def sort(self, reverse=False):
        values = list(self)
        values.sort(reverse=reverse)
        self.clear()
        for value in values:
            self.append(value)
        if self.auto_sync:
            self.save_pyhold()

    def __eq__(self, other):
        if not isinstance(other, pyholdlinkedlist):
            return False
        if len(self) != len(other):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True
    
    def __add__(self, other):
        if not isinstance(other, pyholdlinkedlist):
            raise TypeError(f"Can only concatenate pyholdlinkedlist (not \"{type(other).__name__}\") to pyholdlinkedlist")
        result = pyholdlinkedlist()
        result.extend(self)
        result.extend(other)
        return result
    
    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply pyholdlinkedlist by an integer")
        if other < 0:
            raise ValueError("Can only multiply pyholdlinkedlist by a positive integer")
        result = pyholdlinkedlist()
        for i in range(other):
            result.extend(self)
        return result
    
    def show_gui(self):
        # Main window setup
        self.root = tk.Tk()
        self.root.title(f"pyhold Linked List - {self.filename}")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title and info
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="pyhold Linked List Manager", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        info_label = ttk.Label(title_frame, text=f"File: {self.filename} | Items: {len(self)}")
        info_label.pack(side=tk.RIGHT)
        self.info_label = info_label
        
        # Left panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Index section
        ttk.Label(control_frame, text="Index:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.index_entry = ttk.Entry(control_frame, width=20)
        self.index_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Value section
        ttk.Label(control_frame, text="Value:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.value_text = tk.Text(control_frame, width=20, height=4, wrap=tk.WORD)
        self.value_text.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Value type selection
        ttk.Label(control_frame, text="Type:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.type_var = tk.StringVar(value="str")
        type_combo = ttk.Combobox(control_frame, textvariable=self.type_var, 
                                  values=["str", "int", "float", "bool", "list", "dict", "tuple"], 
                                  state="readonly", width=17)
        type_combo.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=6, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(btn_frame, text="Set at Index", command=self.set_at_index).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="Insert at Index", command=self.insert_at_index).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="Append", command=self.append_value).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_view).pack(fill=tk.X, pady=(0, 10))
        
        # File operations
        ttk.Separator(control_frame, orient='horizontal').grid(row=7, column=0, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(control_frame, text="File Operations:", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        
        file_btn_frame = ttk.Frame(control_frame)
        file_btn_frame.grid(row=9, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(file_btn_frame, text="Save", command=self.manual_save).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(file_btn_frame, text="Reload", command=self.manual_reload).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(file_btn_frame, text="Export JSON", command=self.export_json).pack(fill=tk.X, pady=(0, 5))
        
        # Search section
        ttk.Separator(control_frame, orient='horizontal').grid(row=10, column=0, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(control_frame, text="Search:", font=('Arial', 10, 'bold')).grid(row=11, column=0, sticky=tk.W, pady=(0, 5))
        
        self.search_entry = ttk.Entry(control_frame, width=20)
        self.search_entry.grid(row=12, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.search_entry.bind('<KeyRelease>', self.filter_items)
        
        ttk.Button(control_frame, text="Clear Search", command=self.clear_search).grid(row=13, column=0, sticky=(tk.W, tk.E))
        
        # Right panel - Data display
        data_frame = ttk.LabelFrame(main_frame, text="Linked List Data", padding="10")
        data_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        # Treeview for better data display
        columns = ('Index', 'Value', 'Type')
        self.tree = ttk.Treeview(data_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        self.tree.heading('Index', text='Index')
        self.tree.heading('Value', text='Value')
        self.tree.heading('Type', text='Type')
        
        self.tree.column('Index', width=80, minwidth=60)
        self.tree.column('Value', width=400, minwidth=200)
        self.tree.column('Type', width=80, minwidth=60)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(data_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind events
        self.tree.bind('<ButtonRelease-1>', self.on_item_select)
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)
        
        # Initial population
        self.refresh_view()
        
        # Start the GUI
        self.root.mainloop()
    
    def set_at_index(self):
        index_str = self.index_entry.get().strip()
        value_str = self.value_text.get(1.0, tk.END).strip()
        value_type = self.type_var.get()
        
        if not index_str:
            messagebox.showerror("Error", "Index cannot be empty!")
            return
        
        try:
            index = int(index_str)
            if index < 0:
                messagebox.showerror("Error", "Index must be non-negative!")
                return
            
            # Convert value based on type
            if value_type == "int":
                value = int(value_str)
            elif value_type == "float":
                value = float(value_str)
            elif value_type == "bool":
                value = value_str.lower() in ('true', '1', 'yes', 'on')
            elif value_type in ["list", "dict", "tuple"]:
                value = ast.literal_eval(value_str)
                if value_type == "tuple":
                    value = tuple(value)
            else:  # str
                value = value_str
            
            # Set the value at index
            self[index] = value
            self.refresh_view()
            self.status_label.config(text=f"Set value at index {index}")
            
            # Clear inputs
            self.index_entry.delete(0, tk.END)
            self.value_text.delete(1.0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Index must be a valid integer!")
        except IndexError as e:
            messagebox.showerror("Error", f"Index out of range: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid value for type {value_type}: {str(e)}")
    
    def insert_at_index(self):
        index_str = self.index_entry.get().strip()
        value_str = self.value_text.get(1.0, tk.END).strip()
        value_type = self.type_var.get()
        
        if not index_str:
            messagebox.showerror("Error", "Index cannot be empty!")
            return
        
        try:
            index = int(index_str)
            if index < 0:
                messagebox.showerror("Error", "Index must be non-negative!")
                return
            
            # Convert value based on type
            if value_type == "int":
                value = int(value_str)
            elif value_type == "float":
                value = float(value_str)
            elif value_type == "bool":
                value = value_str.lower() in ('true', '1', 'yes', 'on')
            elif value_type in ["list", "dict", "tuple"]:
                value = ast.literal_eval(value_str)
                if value_type == "tuple":
                    value = tuple(value)
            else:  # str
                value = value_str
            
            # Insert the value at index
            self.insert(index, value)
            self.refresh_view()
            self.status_label.config(text=f"Inserted value at index {index}")
            
            # Clear inputs
            self.index_entry.delete(0, tk.END)
            self.value_text.delete(1.0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Index must be a valid integer!")
        except IndexError as e:
            messagebox.showerror("Error", f"Index out of range: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid value for type {value_type}: {str(e)}")
    
    def append_value(self):
        value_str = self.value_text.get(1.0, tk.END).strip()
        value_type = self.type_var.get()
        
        try:
            # Convert value based on type
            if value_type == "int":
                value = int(value_str)
            elif value_type == "float":
                value = float(value_str)
            elif value_type == "bool":
                value = value_str.lower() in ('true', '1', 'yes', 'on')
            elif value_type in ["list", "dict", "tuple"]:
                value = ast.literal_eval(value_str)
                if value_type == "tuple":
                    value = tuple(value)
            else:  # str
                value = value_str
            
            # Append the value
            self.append(value)
            self.refresh_view()
            self.status_label.config(text=f"Appended value: {value}")
            
            # Clear inputs
            self.value_text.delete(1.0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid value for type {value_type}: {str(e)}")
    
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No item selected!")
            return
        
        item = self.tree.item(selected[0])
        index = int(item['values'][0])
        
        if messagebox.askyesno("Confirm", f"Delete item at index {index}?"):
            try:
                del self[index]
                self.refresh_view()
                self.status_label.config(text=f"Deleted item at index {index}")
            except IndexError:
                messagebox.showerror("Error", f"Index {index} not found!")
    
    def clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all data? This cannot be undone!"):
            self.clear()
            self.refresh_view()
            self.status_label.config(text="All data cleared")
    
    def refresh_view(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add current items
        search_term = self.search_entry.get().lower() if hasattr(self, 'search_entry') else ""
        
        for i, value in enumerate(self):
            if not search_term or search_term in str(value).lower():
                # Truncate long values for display
                display_value = str(value)
                if len(display_value) > 100:
                    display_value = display_value[:97] + "..."
                
                self.tree.insert('', tk.END, values=(i, display_value, type(value).__name__))
        
        # Update info label
        if hasattr(self, 'info_label'):
            self.info_label.config(text=f"File: {self.filename} | Items: {len(self)}")
    
    def on_item_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            index = int(item['values'][0])
            value = self[index]
            
            self.index_entry.delete(0, tk.END)
            self.index_entry.insert(0, str(index))
            
            self.value_text.delete(1.0, tk.END)
            if type(value).__name__ in ["dict", "list", "tuple"]:
                self.value_text.insert(1.0, json.dumps(value, indent=2))
            else:
                self.value_text.insert(1.0, str(value))
            
            self.type_var.set(type(value).__name__)
    
    def on_item_double_click(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            index = int(item['values'][0])
            value = self[index]
            
            # Show full value in popup
            popup = tk.Toplevel(self.root)
            popup.title(f"Value at index: {index}")
            popup.geometry("600x400")
            
            text_widget = tk.Text(popup, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(popup, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            if type(value).__name__ in ["dict", "list", "tuple"]:
                text_widget.insert(1.0, json.dumps(value, indent=2))
            else:
                text_widget.insert(1.0, str(value))
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def filter_items(self, event):
        self.refresh_view()
    
    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.refresh_view()
    
    def manual_save(self):
        try:
            self.save_pyhold()
            self.status_label.config(text="Data saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def manual_reload(self):
        try:
            self.load_pyhold()
            self.refresh_view()
            self.status_label.config(text="Data reloaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reload: {str(e)}")
    
    def export_json(self):
        try:
            data = list(self)
            json_filename = self.filename.replace('.xml', '.json')
            
            with open(json_filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.status_label.config(text=f"Exported to {json_filename}")
            messagebox.showinfo("Success", f"Data exported to {json_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")