#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python wrapper for C implementations used in Project Euler problem 95 (Amicable Chains).

Exposes:
- longest_amicable_chain(max_num: int) -> tuple[int, int]
  Returns (longest_length, smallest_member) for amicable chains with members ≤ max_num.
"""
from __future__ import annotations

import ctypes

from euler_solver.c_libs import import_c_lib

__all__ = [
    'longest_amicable_chain',
]

# Load the C library built from src/p0095.c -> libs/lib_p0095.so
_c_lib = import_c_lib('lib_p0095')

# Bind C function: void longest_amicable_chain(int max_num, int* out_length, int* out_smallest)
_c_func = getattr(_c_lib, 'longest_amicable_chain')
_c_func.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
_c_func.restype = None


def longest_amicable_chain(max_num: int) -> tuple[int, int]:
    if not isinstance(max_num, int) or max_num <= 1:
        raise ValueError('max_num must be an integer greater than 1')
    out_len = ctypes.c_int(0)
    out_sm = ctypes.c_int(0)
    _c_func(int(max_num), ctypes.byref(out_len), ctypes.byref(out_sm))
    return int(out_len.value), int(out_sm.value)
