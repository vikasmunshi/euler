#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python wrapper for C implementations used in Project Euler problem 642.

Exposes:
- euler642(n: int, modulo: int) -> int
"""
from __future__ import annotations

import ctypes

from euler_solver.c_libs.wrapper import import_c_lib

__all__ = [
    'euler642',
]

# Load the C library built from src/p0642.c -> libs/lib_p0642.so
_c_lib = import_c_lib('lib_p0642')

# Bind C function: long long euler642(unsigned long long n, int modulo)
_c_func = getattr(_c_lib, 'euler642')
_c_func.argtypes = [ctypes.c_ulonglong, ctypes.c_int]
_c_func.restype = ctypes.c_longlong


def euler642(n: int, modulo: int) -> int:
    if not isinstance(n, int) or n < 0:
        raise ValueError('n must be a non-negative integer')
    if not isinstance(modulo, int) or modulo <= 0:
        raise ValueError('modulo must be a positive integer')
    return int(_c_func(ctypes.c_ulonglong(n), ctypes.c_int(modulo)))
