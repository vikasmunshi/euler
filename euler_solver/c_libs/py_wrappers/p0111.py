#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python wrapper for C implementations used in Project Euler problem 111. """
from __future__ import annotations

import ctypes

from euler_solver.c_libs.wrapper import import_c_lib

__all__ = [
    'euler111',
]

# Ensure primes library is loaded for symbol resolution
_primes_lib = import_c_lib('lib_primes')

# Load the C library built from src/p0111.c -> libs/lib_p0111.so
_c_lib = import_c_lib('lib_p0111')

# Bind C function
_c_func = getattr(_c_lib, 'euler111')
_c_func.argtypes = [ctypes.c_int, ctypes.c_int]
_c_func.restype = ctypes.c_longlong


def euler111(n: int, print_working: bool) -> int:
    if not (4 <= n <= 16):
        raise ValueError('n must be between 4 and 16')
    return int(_c_func(ctypes.c_int(n), ctypes.c_int(1 if print_working else 0)))
