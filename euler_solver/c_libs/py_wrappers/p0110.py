#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python wrapper for C implementations used in Project Euler problem 110.

Exposes:
- euler110(min_number_of_solutions: int) -> int
"""
from __future__ import annotations

import ctypes
import sys

from euler_solver.c_libs.wrapper import import_c_lib

__all__ = [
    'euler110',
]

# Load the C library built from src/p0110.c -> libs/lib_p0110.so
_c_lib = import_c_lib('lib_p0110')

# Bind C function
_c_func = getattr(_c_lib, 'euler110')
_c_func.argtypes = [ctypes.c_int]
_c_func.restype = ctypes.c_longlong


def euler110(min_number_of_solutions: int) -> int:
    if not (0 < min_number_of_solutions < sys.maxsize):
        raise ValueError(f'number must be between 0 and {sys.maxsize}')
    return int(_c_func(ctypes.c_int(min_number_of_solutions)))
