#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Python wrapper for C implementations of functions used in Project Euler problem 81, 82, and 83. """
from __future__ import annotations

import ctypes

from euler_solver.c_libs import to_bytes, import_c_lib

__all__ = [
    'path_sum_two_ways',
    'path_sum_three_ways',
    'path_sum_four_ways',
]

# Load the C library built from src/matrix_path_sums.c -> libs/lib_matrix_path_sums.so
_c_lib = import_c_lib('lib_matrix_path_sums')

# Bindings
_path_sum_two_c = _c_lib.path_sum_two_ways_from_csv
_path_sum_two_c.argtypes = [ctypes.c_char_p]
_path_sum_two_c.restype = ctypes.c_longlong

_path_sum_three_c = _c_lib.path_sum_three_ways_from_csv
_path_sum_three_c.argtypes = [ctypes.c_char_p]
_path_sum_three_c.restype = ctypes.c_longlong

_path_sum_four_c = _c_lib.path_sum_four_ways_from_csv
_path_sum_four_c.argtypes = [ctypes.c_char_p]
_path_sum_four_c.restype = ctypes.c_longlong


def path_sum_two_ways(content: str) -> int:
    """Compute minimal path sum with moves right/down (Problem 81) from CSV matrix string."""
    return int(_path_sum_two_c(to_bytes(content)))


def path_sum_three_ways(content: str) -> int:
    """Compute minimal path sum with moves up/down/right (Problem 82) from CSV matrix string."""
    return int(_path_sum_three_c(to_bytes(content)))


def path_sum_four_ways(content: str) -> int:
    """Compute minimal path sum with moves in four directions (Problem 83) from CSV matrix string."""
    return int(_path_sum_four_c(to_bytes(content)))
