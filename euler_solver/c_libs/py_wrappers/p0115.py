#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python wrapper for C implementations used in Project Euler problem 115. """
from __future__ import annotations

import ctypes

from euler_solver.c_libs.wrapper import import_c_lib

__all__ = [
    'fill_count',
]

# Load the C library built from src/p0115.c -> libs/lib_p0115.so
_c_lib = import_c_lib('lib_p0115')

# Bind C function with signature: long long fill_count(int m, int n)
_c_func = getattr(_c_lib, 'fill_count')
_c_func.argtypes = [ctypes.c_int, ctypes.c_int]
_c_func.restype = ctypes.c_longlong


def fill_count(m: int, n: int) -> int:
    return int(_c_func(ctypes.c_int(m), ctypes.c_int(n)))
