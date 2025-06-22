from pyhold.pyholdkeyvalue import pyholdkeyvalue
from pyhold.pyholdlinkedlist import pyholdlinkedlist

class pyhold:
    def __new__(cls, filename="pyhold.xml", mode="keyvalue", auto_sync=True, auto_reload=True):
        if mode == "keyvalue":
            return pyholdkeyvalue(filename, auto_sync, auto_reload)
        elif mode == "linkedlist":
            return pyholdlinkedlist(filename, auto_sync, auto_reload)
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")