import pytest
import os
import tempfile
import xml.etree.ElementTree as ET
from unittest.mock import patch, mock_open
import json

# Assuming the Datalink class is in a file called datalink.py
# If it's in a different file, adjust the import accordingly
from Datalink import Datalink


class TestDatalinkInitialization:
    """Test Datalink initialization and configuration"""
    
    def test_default_initialization(self):
        """Test default initialization parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = os.path.join(temp_dir, "test.xml")
            dl = Datalink(filename=filename)
            
            assert dl.filename == filename
            assert dl.mode == "keyvalue"
            assert dl.auto_sync is True
            assert dl.auto_reload is True
            assert isinstance(dl.volatileMem, list)
    
    def test_custom_initialization(self):
        """Test initialization with custom parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = os.path.join(temp_dir, "custom.xml")
            dl = Datalink(filename=filename, mode="keyvalue", auto_sync=False, auto_reload=False)
            
            assert dl.filename == filename
            assert dl.mode == "keyvalue"
            assert dl.auto_sync is False
            assert dl.auto_reload is False
    
    def test_initialization_with_existing_file(self):
        """Test initialization when XML file already exists"""
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = os.path.join(temp_dir, "existing.xml")
            
            # Create a sample XML file
            root = ET.Element("datalink")
            keyval = ET.SubElement(root, "keyval")
            key_elem = ET.SubElement(keyval, "key")
            key_elem.text = "test_key"
            value_elem = ET.SubElement(keyval, "value")
            value_elem.text = "test_value"
            value_elem.set("dtype", "str")
            
            tree = ET.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            
            dl = Datalink(filename=filename)
            assert len(dl.volatileMem) == 1
            assert dl["test_key"] == "test_value"
    
    def test_initialization_no_auto_reload(self):
        """Test initialization with auto_reload=False"""
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = os.path.join(temp_dir, "no_reload.xml")
            dl = Datalink(filename=filename, auto_reload=False)
            
            assert len(dl.volatileMem) == 0


class TestDatalinkKeyValueOperations:
    """Test key-value operations"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.filename = os.path.join(self.temp_dir, "test.xml")
        self.dl = Datalink(filename=self.filename, auto_sync=False)
    
    def teardown_method(self):
        """Cleanup after each test method"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_write_new_key(self):
        """Test writing a new key-value pair"""
        self.dl.write("new_key", "new_value")
        
        assert len(self.dl.volatileMem) == 1
        assert self.dl["new_key"] == "new_value"
    
    def test_write_update_existing_key(self):
        """Test updating an existing key"""
        self.dl.write("key1", "value1")
        self.dl.write("key1", "updated_value")
        
        assert len(self.dl.volatileMem) == 1
        assert self.dl["key1"] == "updated_value"
    
    def test_write_missing_parameters(self):
        """Test write method with missing parameters"""
        with pytest.raises(ValueError, match="Key must be provided"):
            self.dl.write(value="value1")

        with pytest.raises(ValueError, match="Key must be provided"):
            self.dl.write()

    
    def test_getitem_existing_key(self):
        """Test getting value for existing key"""
        self.dl.write("test_key", "test_value")
        assert self.dl["test_key"] == "test_value"
    
    def test_getitem_nonexistent_key(self):
        """Test getting value for non-existent key"""
        with pytest.raises(KeyError, match="Key 'nonexistent' not found"):
            _ = self.dl["nonexistent"]
    
    def test_setitem(self):
        """Test setting item using square bracket notation"""
        self.dl["new_key"] = "new_value"
        assert self.dl["new_key"] == "new_value"
        
        # Test updating existing key
        self.dl["new_key"] = "updated_value"
        assert self.dl["new_key"] == "updated_value"
    
    def test_contains(self):
        """Test __contains__ method"""
        self.dl.write("existing_key", "value")
        
        assert "existing_key" in self.dl
        assert "nonexistent_key" not in self.dl
    
    def test_len(self):
        """Test __len__ method"""
        assert len(self.dl) == 0
        
        self.dl.write("key1", "value1")
        assert len(self.dl) == 1
        
        self.dl.write("key2", "value2")
        assert len(self.dl) == 2
    
    def test_iter(self):
        """Test __iter__ method"""
        self.dl.write("key1", "value1")
        self.dl.write("key2", "value2")
        
        keys = [item.key for item in self.dl]
        values = [item.value for item in self.dl]
        
        assert "key1" in keys
        assert "key2" in keys
        assert "value1" in values
        assert "value2" in values
    
    def test_pop_existing_key(self):
        """Test popping an existing key"""
        self.dl.write("key1", "value1")
        self.dl.write("key2", "value2")
        
        popped_value = self.dl.pop("key1")
        
        assert popped_value == "value1"
        assert len(self.dl) == 1
        assert "key1" not in self.dl
        assert "key2" in self.dl
    
    def test_pop_nonexistent_key(self):
        """Test popping a non-existent key"""
        with pytest.raises(KeyError, match="Key 'nonexistent' not found"):
            self.dl.pop("nonexistent")


class TestDatalinkDataTypes:
    """Test handling of different data types"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.filename = os.path.join(self.temp_dir, "test.xml")
        self.dl = Datalink(filename=self.filename, auto_sync=False)
    
    def teardown_method(self):
        """Cleanup after each test method"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_string_type(self):
        """Test string data type"""
        self.dl.write("str_key", "string_value")
        assert self.dl["str_key"] == "string_value"
        assert self.dl.volatileMem[0].dtype == "str"
    
    def test_integer_type(self):
        """Test integer data type"""
        self.dl.write("int_key", 42)
        assert self.dl["int_key"] == 42
        assert self.dl.volatileMem[0].dtype == "int"
    
    def test_float_type(self):
        """Test float data type"""
        self.dl.write("float_key", 3.14)
        assert self.dl["float_key"] == 3.14
        assert self.dl.volatileMem[0].dtype == "float"
    
    def test_boolean_type(self):
        """Test boolean data type"""
        self.dl.write("bool_key", True)
        assert self.dl["bool_key"] is True
        assert self.dl.volatileMem[0].dtype == "bool"
        
        self.dl.write("bool_key2", False)
        assert self.dl["bool_key2"] is False
    
    def test_list_type(self):
        """Test list data type"""
        test_list = [1, 2, 3, "four"]
        self.dl.write("list_key", test_list)
        assert self.dl["list_key"] == test_list
        assert self.dl.volatileMem[0].dtype == "list"
    
    def test_dict_type(self):
        """Test dictionary data type"""
        test_dict = {"a": 1, "b": 2, "c": "three"}
        self.dl.write("dict_key", test_dict)
        assert self.dl["dict_key"] == test_dict
        assert self.dl.volatileMem[0].dtype == "dict"
    
    def test_tuple_type(self):
        """Test tuple data type"""
        test_tuple = (1, 2, "three")
        self.dl.write("tuple_key", test_tuple)
        assert self.dl["tuple_key"] == test_tuple
        assert self.dl.volatileMem[0].dtype == "tuple"


class TestDatalinkFileOperations:
    """Test file save and load operations"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.filename = os.path.join(self.temp_dir, "test.xml")
    
    def teardown_method(self):
        """Cleanup after each test method"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_datalink(self):
        """Test saving data to XML file"""
        dl = Datalink(filename=self.filename, auto_sync=False)
        dl.write("key1", "value1")
        dl.write("key2", 42)
        dl.write("key3", True)
        
        dl.save_datalink()
        
        # Verify file exists and has correct structure
        assert os.path.exists(self.filename)
        
        tree = ET.parse(self.filename)
        root = tree.getroot()
        
        assert root.tag == "datalink"
        keyvals = root.findall("keyval")
        assert len(keyvals) == 3
    
    def test_load_datalink(self):
        """Test loading data from XML file"""
        # First create and save some data
        dl1 = Datalink(filename=self.filename, auto_sync=False)
        dl1.write("key1", "value1")
        dl1.write("key2", 42)
        dl1.write("key3", [1, 2, 3])
        dl1.save_datalink()
        
        # Create new instance and load data
        dl2 = Datalink(filename=self.filename, auto_reload=False)
        dl2.load_datalink()
        
        assert len(dl2) == 3
        assert dl2["key1"] == "value1"
        assert dl2["key2"] == 42
        assert dl2["key3"] == [1, 2, 3]
    
    def test_load_nonexistent_file(self):
        """Test loading from non-existent file"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.xml")
        dl = Datalink(filename=nonexistent_file, auto_reload=False)
        
        # Should not raise an error
        dl.load_datalink()
        assert len(dl) == 0
    
    def test_auto_sync_enabled(self):
        """Test automatic syncing when enabled"""
        dl = Datalink(filename=self.filename, auto_sync=True)
        
        # Write operation should automatically save
        dl.write("auto_key", "auto_value")
        
        # Verify file was created
        assert os.path.exists(self.filename)
        
        # Load with new instance to verify data was saved
        dl2 = Datalink(filename=self.filename)
        assert dl2["auto_key"] == "auto_value"
    
    def test_auto_sync_disabled(self):
        """Test no automatic syncing when disabled"""
        dl = Datalink(filename=self.filename, auto_sync=False)
        
        # Write operation should not automatically save
        dl.write("no_auto_key", "no_auto_value")
        
        # File should not exist yet
        assert not os.path.exists(self.filename)
    
    def test_complex_data_persistence(self):
        """Test persistence of complex data types"""
        dl1 = Datalink(filename=self.filename, auto_sync=False)
        
        test_data = {
            "string": "test_string",
            "integer": 123,
            "float": 45.67,
            "boolean_true": True,
            "boolean_false": False,
            "list": [1, "two", 3.0],
            "dict": {"nested": "value", "number": 99},
            "tuple": (1, 2, "three")
        }
        
        for key, value in test_data.items():
            dl1.write(key, value)
        
        dl1.save_datalink()
        
        # Load with new instance
        dl2 = Datalink(filename=self.filename)
        
        for key, expected_value in test_data.items():
            assert dl2[key] == expected_value


class TestDatalinkEdgeCases:
    """Test edge cases and error conditions"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.filename = os.path.join(self.temp_dir, "test.xml")
    
    def teardown_method(self):
        """Cleanup after each test method"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_key(self):
        """Test handling of empty key"""
        dl = Datalink(filename=self.filename, auto_sync=False)
        dl.write("", "empty_key_value")
        assert dl[""] == "empty_key_value"
    
    def test_none_values(self):
        """Test handling of None values"""
        dl = Datalink(filename=self.filename, auto_sync=False)
        dl.write("none_key", None)
        assert dl["none_key"] is None
    
    def test_unicode_characters(self):
        """Test handling of Unicode characters"""
        dl = Datalink(filename=self.filename, auto_sync=False)
        unicode_value = "Hello 世界 🌍"
        dl.write("unicode_key", unicode_value)
        assert dl["unicode_key"] == unicode_value
    
    def test_large_data(self):
        """Test handling of large data"""
        dl = Datalink(filename=self.filename, auto_sync=False)
        large_list = list(range(1000))
        dl.write("large_key", large_list)
        assert dl["large_key"] == large_list
    
    def test_special_characters_in_keys(self):
        """Test keys with special characters"""
        dl = Datalink(filename=self.filename, auto_sync=False)
        special_key = "key with spaces & symbols!@#$%"
        dl.write(special_key, "special_value")
        assert dl[special_key] == "special_value"
    
    def test_overwrite_different_types(self):
        """Test overwriting value with different data type"""
        dl = Datalink(filename=self.filename, auto_sync=False)
        
        dl.write("type_key", "string")
        assert dl["type_key"] == "string"
        assert dl.volatileMem[0].dtype == "str"
        
        dl.write("type_key", 42)
        assert dl["type_key"] == 42
        assert dl.volatileMem[0].dtype == "int"


class TestDatalinkNotImplemented:
    """Test methods that should raise NotImplementedError for non-keyvalue modes"""
    
    def test_not_implemented_methods(self):
        """Test that methods raise NotImplementedError for unsupported modes"""
        # Note: Since the current implementation only supports keyvalue mode,
        # we can't actually test other modes. This is a placeholder for future modes.
        pass


class TestDatalinkKeyvalNode:
    """Test the internal __keyvalNode class"""
    
    def test_keyval_node_creation(self):
        """Test creation of keyval nodes"""
        dl = Datalink(filename="test.xml", auto_sync=False)
        node = dl._Datalink__keyvalNode("test_key", "test_value")
        
        assert node.key == "test_key"
        assert node.value == "test_value"
        assert node.dtype == "str"
    
    def test_keyval_node_different_types(self):
        """Test keyval nodes with different data types"""
        dl = Datalink(filename="test.xml", auto_sync=False)
        
        int_node = dl._Datalink__keyvalNode("int_key", 42)
        assert int_node.dtype == "int"
        
        float_node = dl._Datalink__keyvalNode("float_key", 3.14)
        assert float_node.dtype == "float"
        
        bool_node = dl._Datalink__keyvalNode("bool_key", True)
        assert bool_node.dtype == "bool"
        
        list_node = dl._Datalink__keyvalNode("list_key", [1, 2, 3])
        assert list_node.dtype == "list"


# Integration tests
class TestDatalinkIntegration:
    """Integration tests for complete workflows"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.filename = os.path.join(self.temp_dir, "integration_test.xml")
    
    def teardown_method(self):
        """Cleanup after each test method"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_workflow(self):
        """Test complete workflow: create, modify, save, load, modify again"""
        # Phase 1: Create and populate
        dl1 = Datalink(filename=self.filename, auto_sync=True)
        dl1["name"] = "John"
        dl1["age"] = 25
        dl1["hobbies"] = ["reading", "coding"]
        
        # Phase 2: Load in new instance and verify
        dl2 = Datalink(filename=self.filename)
        assert dl2["name"] == "John"
        assert dl2["age"] == 25
        assert dl2["hobbies"] == ["reading", "coding"]
        
        # Phase 3: Modify and save
        dl2["age"] = 26
        dl2["city"] = "New York"
        del dl2["hobbies"]
        
        # Phase 4: Load again and verify changes
        dl3 = Datalink(filename=self.filename)
        assert dl3["name"] == "John"
        assert dl3["age"] == 26
        assert dl3["city"] == "New York"
        assert "hobbies" not in dl3
    
    def test_concurrent_access_simulation(self):
        """Simulate concurrent access by multiple Datalink instances"""
        # Instance 1 writes data
        dl1 = Datalink(filename=self.filename, auto_sync=True)
        dl1["shared_key"] = "initial_value"
        
        # Instance 2 reads and modifies
        dl2 = Datalink(filename=self.filename, auto_sync=True)
        assert dl2["shared_key"] == "initial_value"
        dl2["shared_key"] = "modified_value"
        
        # Instance 3 reads the modification
        dl3 = Datalink(filename=self.filename)
        assert dl3["shared_key"] == "modified_value"


if __name__ == "__main__":
    pytest.main([__file__])