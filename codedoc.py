"""
Command Line tool for Python code documentation.
"""
import ast
import os
import io
import sys
from os.path import exists, basename, isdir
import pathlib
import inspect
import argparse
import logging
import importlib
import importlib.util as imutil
from types import ModuleType
from typing import Union, Any
import dataclasses

from exceptions import InvalidModuleError, CallableTypeError


class CodeDoc:
    """
    Python module object
    """
    module = None

    """
    Original source code of the module
    """
    orig_source = b""

    """
    Updated source code of the module with Docstrings
    """
    output = ""

    "Module callables"
    callables = {}

    def __init__(self, file: str) -> None:
        self.file = file

        self.output_buffer = None

        self.__verify_module()
        self.find_callables()
        self.update_callables()
    
    def __verify_module(self):
        try:
            self.module = importlib.import_module(self.file)
        except ModuleNotFoundError:
            raise ModuleNotFoundError(f"{self.file} could not be found.")
        
        self.orig_source = inspect.getsource(self.module).encode()
        self.output = self.orig_source.decode()
    
    def find_callables(self) -> None:
        """
        Finds all the callable objects within the given module
        """
        members = set(m for m in inspect.getmembers(self.module) \
                      if not m[0].startswith('__') and not m[0].endswith('__'))
        self.callables = {name: obj for name, obj in members if callable(obj)}
    
    # @staticmethod
    # def get_params(_callable):
    #     sig = inspect.signature(_callable)
    #     return sig.parameters

    def update_callables(self):
        """
        Add the docstring to the callables
        """
        for name, obj in self.callables.items():
            self.add_doc(obj)
        
        with open(self.module.__file__, 'w+') as f:
            f.write(self.output)
 
    
    def add_doc(self, obj):
        tree = ast.parse(inspect.getsource(obj))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == obj.__name__:
                node_1 = node.body[0]
                if isinstance(node_1, ast.Expr):
                    # Already has some Doc string
                    # print(f"{obj.__name__} already docked")
                    break
                else:
                    _doc = ast.Expr(value=ast.Constant(s="Added by CodeDoc"))
                    node.body.insert(0, _doc)
                    break

        updated = ast.unparse(tree)
        self.write_updated(obj.__name__, updated)
    
    def write_updated(self, name, updated_source) -> None:
        old_content = inspect.getsource(self.callables[name])
        final = self.output.replace(old_content, updated_source)
        self.output = final


def main():
    parser = argparse.ArgumentParser(
        prog="python -m codedoc",
        description="Documentation for Python code"
    )

    parser.add_argument('--file', '-f', help="Path to the Python module")
    options = parser.parse_args()

    doc = CodeDoc(options.file)


if __name__ == "__main__":
    main()