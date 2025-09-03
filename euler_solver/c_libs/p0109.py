#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python wrapper for C implementations used in Project Euler problem 109.

Exposes:
- euler109(max_limit: int) -> int
"""
from __future__ import annotations

import ctypes
import sys

from euler_solver.c_libs import import_c_lib

__all__ = [
    'euler109',
]

# Load the C library built from src/p0109.c -> libs/lib_p0109.so
_c_lib = import_c_lib('lib_p0109')

# Bind C function
_c_func = getattr(_c_lib, 'euler109')
_c_func.argtypes = [ctypes.c_int]
_c_func.restype = ctypes.c_longlong


def euler109(max_limit: int) -> int:
    if not (0 < max_limit < sys.maxsize):
        raise ValueError(f'number must be between 0 and {sys.maxsize}')
    return int(_c_func(ctypes.c_int(max_limit)))
