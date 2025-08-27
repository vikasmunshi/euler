#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Python wrapper for C implementations of functions used in Project Euler problem 78. """
from __future__ import annotations

import ctypes
import sys

from euler_solver.c_libs import import_c_lib

ERROR_GENERAL_FAILURE = 1  # not used explicitly; C returns -1 on failure
MAX_VALID_INPUT = sys.maxsize  # guard for unreasonable divisors

# Import the C library and function
c_lib = import_c_lib('lib_p0078')

_c_least_n = getattr(c_lib, 'least_number_with_partitions_divisible_by')
_c_least_n.argtypes = [ctypes.c_int]
_c_least_n.restype = ctypes.c_int


def least_number_with_partitions_divisible_by(divisor: int) -> int:
    """
    Return the least n such that the partition number p(n) is divisible by 'divisor'.

    Parameters:
        divisor (int): Positive modulus (e.g., 1_000_000 for Euler 78)

    Returns:
        int: The least n where p(n) % divisor == 0. Raises ValueError for invalid input.
    """
    if not (isinstance(divisor, int) and 0 < divisor < MAX_VALID_INPUT):
        raise ValueError(f'divisor must be a positive int less than {MAX_VALID_INPUT}')
    n = _c_least_n(ctypes.c_int(divisor))
    if n < 0:
        raise RuntimeError('C computation failed')
    return int(n)
