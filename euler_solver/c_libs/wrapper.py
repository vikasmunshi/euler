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
from functools import wraps
from importlib import import_module
from types import ModuleType
from typing import Any, Callable, ClassVar, ParamSpec, TypeVar

from euler_solver.logger import logger

lib_dir: str = os.path.join(os.path.dirname(__file__), 'libs')
if sys.platform.startswith('win'):
    lib_ext = '.dll'
elif sys.platform.startswith('darwin'):
    lib_ext = '.dylib'
else:
    lib_ext = '.so'
src_dir: str = os.path.join(os.path.dirname(__file__), 'src')


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
        lib_path = os.path.join(lib_dir, lib_name + lib_ext)
        # Load with RTLD_GLOBAL to allow symbol resolution across shared libs
        mode = getattr(ctypes, 'RTLD_GLOBAL', None)
        lib = ctypes.CDLL(lib_path, mode=mode) if mode is not None else ctypes.CDLL(lib_path)
        return lib
    except OSError as e:
        raise ImportError(f"Failed to load C library '{lib_name}'. "
                          f"Make sure the library is compiled and installed correctly: {e}")


PS = ParamSpec('PS')
RT = TypeVar('RT')
FS = Callable[PS, RT]


class WrappedCFunction:
    use_py_func: ClassVar[bool] = False

    def __init__(self, *, py_func: FS, c_func: FS | None) -> None:
        self.c_func: FS = py_func if c_func is None else c_func
        self.py_func: FS = py_func

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.__class__.use_py_func:
            return self.py_func(*args, **kwargs)
        return self.c_func(*args, **kwargs)


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

    def decorator(py_func: FS[PS, RT]) -> FS[PS, RT]:
        try:
            module: ModuleType = import_module(f'euler_solver.c_libs.py_wrappers.{module_name}')
            c_func: FS[PS, RT] = getattr(module, py_func.__name__)
        except (AttributeError, ImportError) as e:
            logger.error(f"Failed to find C implementation '{module_name}': {e}")
            return wraps(py_func)(WrappedCFunction(py_func=py_func, c_func=None))
        if (py_sig := inspect.signature(py_func)) != (c_sig := inspect.signature(c_func)):
            raise TypeError(f"Function signatures don't match: Python {py_sig} != C {c_sig}")
        return wraps(py_func)(WrappedCFunction(py_func=py_func, c_func=c_func))

    return decorator


def set_use_py_func(use_py_func: bool) -> None:
    WrappedCFunction.use_py_func = use_py_func


def get_use_py_func() -> bool:
    return WrappedCFunction.use_py_func
