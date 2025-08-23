#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ctypes
import os
import sys
import typing


def import_c_lib(lib_name: str, func_name: str) -> typing.Callable:
    """Import function from compiled C library.

    Args:
        lib_name: Name of the library without extension
        func_name: Name of the function to import

    Returns:
        Callable function from the library

    Raises:
        ImportError: If library or function cannot be loaded
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
        return getattr(lib, func_name)
    except (OSError, AttributeError) as e:
        raise ImportError(f"Failed to load C function '{func_name}' from library '{lib_name}'. "
                          f"Make sure the library is compiled and installed correctly: {e}")
