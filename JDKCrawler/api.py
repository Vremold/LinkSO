import os
import sys
import json

class JavaElement:
    def __init__(self, name, url="", des=""):
        self.name = name
        self.url = url
        self.description = des

class Package(JavaElement):
    def __init__(self, name, url="", des=""):
        super().__init__(name, url, des)
        self.exceptions = []
        self.classes = []
        self.interfaces = []
        self.errors = []
        self.enums = []
        pass

    def add_class(self, clas):
        if isinstance(clas, list):
            self.classes.extend(clas)
        else:
            self.classes.append(clas)   
    def add_exception(self, ex):
        if isinstance(ex, list):
            self.exceptions.extend(ex)
        else:
            self.exceptions.append(ex)
    def add_interface(self, inter):
        if isinstance(inter, list):
            self.interfaces.extend(inter)
        else:
            self.interfaces.append(inter)
    def add_enum(self, enum):
        if isinstance(enum, list):
            self.enums.extend(enum)
        else:
            self.enums.append(enum)
    def add_error(self, error):
        if isinstance(error, list):
            self.errors.extend(error)
        else:
            self.errors.append(error)
    
    def __str__(self):
        return "Package " + self.name

class Interface(JavaElement):
    def __init__(self, name, url="", des=""):
        super().__init__(name, url, des)

        self.methods = []
    
    def __str__(self):
        return "Interface " +  self.name

class EException(JavaElement):
    def __init__(self, name, url="", des=""):
        super().__init__(name, url, des)
    def __str__(self):
        return "Exception " + self.name

class Class(JavaElement):
    def __init__(self, name, url="", des=""):
        super().__init__(name, url, des)

        self.methods = []
    
    def __str__(self):
        return "Class " + self.name

class Enum(JavaElement):
    def __init__(self, name, url="", des=""):
        super().__init__(name, url, des)

    def __str__(self):
        return "Enum " + self.name

class Error(JavaElement):
    def __init__(self, name, url="", des=""):
        super().__init__(name, url, des)

    def __str__(self):
        return "Error " + self.name