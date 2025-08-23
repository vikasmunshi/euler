#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Python wrapper for C implementation of digit factorial chains. """
from __future__ import annotations

import ctypes

from euler_solver.c_libs.import_c_lib import import_c_lib

__all__ = ['count_digit_factorial_max_length_chains_c']

c_func = import_c_lib('libdigit_factorial_chains', 'count_digit_factorial_max_length_chains')
c_func.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
c_func.restype = ctypes.c_int


def count_digit_factorial_max_length_chains_c(max_num: int) -> tuple[int, int]:
    chain_count = ctypes.c_int()
    max_length = ctypes.c_int()
    result = c_func(max_num, ctypes.byref(chain_count), ctypes.byref(max_length))
    if result != 0:
        raise RuntimeError(f'Error calling C function: {result}')
    return chain_count.value, max_length.value
