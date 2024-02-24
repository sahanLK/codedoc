"""
Command Line tool for Python code documentation.
"""
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
    Final output
    """
    output = b""

    "Module callables"
    _callables: dict = {}

    def __init__(self, file: str) -> None:
        self.file = file

        self.output_buffer = None

        self.__verify_module()
        self.find_callables()
        self.add_docstring()
    
    def __verify_module(self):
        try:
            self.module = importlib.import_module(self.file)
        except ModuleNotFoundError:
            raise ModuleNotFoundError(f"{self.file} could not be found.")
    
    def get_members(self):
        members = set(m for m in inspect.getmembers(self.module) \
                      if not m[0].startswith('__') and not m[0].endswith('__'))
        return members
    
    def find_callables(self):
        self._callables = {name: obj for name, obj in self.get_members() if callable(obj)}

    @staticmethod
    def get_params( _callable):
        if not callable(_callable):
            raise CallableTypeError(f"{_callable.__repr__()} is not a callable")
        
        sig = inspect.signature(_callable)
        return sig.parameters

    def add_docstring(self):
        """
        Add the docstring to the callables
        """
        for name, obj in self._callables.items():
            params = self.get_params(obj)
            obj.__doc__ = "Doc string added " + name
            self._callables[name] = obj
    
        for name, obj in self._callables.items():
            print(obj.__doc__)
            print(inspect.getsource(object=obj))
            print("\n")
    


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