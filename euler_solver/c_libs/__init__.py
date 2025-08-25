#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""C library utilities for managing and importing compiled C functions.

This module provides functionality to:
- Import functions from compiled C libraries (.dll, .dylib, .so)
- Wrap C functions with Python decorators for seamless integration
- Handle platform-specific library extensions
"""
from __future__ import annotations

import ctypes
import inspect
import os
import sys
from importlib import import_module
from types import ModuleType
from typing import Callable, ParamSpec, TypeVar


def import_c_lib(lib_name: str) -> ctypes.CDLL:
    """Import a specific function from a compiled C library.

    This function handles platform-specific library extensions and loads
    C functions from compiled libraries located in the 'libs' subdirectory.

    Args:
        lib_name: Name of the library without extension (e.g., 'mylib')
        func_name: Name of the function to import from the library

    Returns:
        Callable: A callable function object from the loaded C library

    Raises:
        ImportError: If the library cannot be found or the function cannot be loaded
    """
    try:
        if sys.platform.startswith('win'):
            lib_ext = '.dll'
        elif sys.platform.startswith('darwin'):
            lib_ext = '.dylib'
        else:
            lib_ext = '.so'
        lib_path = os.path.join(os.path.dirname(__file__), 'libs', lib_name + lib_ext)
        lib = ctypes.CDLL(lib_path)
        return lib
    except OSError as e:
        raise ImportError(f"Failed to load C library '{lib_name}'. "
                          f"Make sure the library is compiled and installed correctly: {e}")


PS = ParamSpec('PS')
RT = TypeVar('RT')
FS = Callable[PS, RT]


def use_wrapped_c_function(module_name: str) -> Callable[[FS[PS, RT]], FS[PS, RT]]:
    """Decorator for wrapping Python functions with their C implementations.

    This decorator imports a C function with the same name as the decorated Python
    function from a specified module and returns it instead of the Python implementation.

    Args:
        module_name: Name of the module containing the Python Wrapper for the C implementation

    Returns:
        Callable: A decorator that replaces the Python function with its C counterpart

    Raises:
        AttributeError: If a function with the same name cannot be found in the specified module,
        ImportError: If the specified module cannot be imported,
        TypeError: If the function signatures don't match.
    """

    def decorator(func: FS[PS, RT]) -> FS[PS, RT]:
        func_name = func.__name__
        module: ModuleType = import_module(f'euler_solver.c_libs.{module_name}')
        wrapped_c_func = getattr(module, func_name)
        if (py_sig := inspect.signature(func)) != (c_sig := inspect.signature(wrapped_c_func)):
            raise TypeError(f"Function signatures don't match: Python {py_sig} != C {c_sig}")
        return wrapped_c_func

    return decorator
