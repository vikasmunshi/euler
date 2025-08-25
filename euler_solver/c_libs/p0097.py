#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python wrapper for C implementations used in Project Euler problem 97.

Exposes:
- large_non_mersenne_prime(num_digits: int, prime: str) -> int
  Computes (A * 2^B + 1) mod 10^num_digits where 'prime' is like '28433 × 2^7830457 + 1'.
"""
from __future__ import annotations

import ctypes

from euler_solver.c_libs import import_c_lib

__all__ = [
    'large_non_mersenne_prime',
]

# Load the C library built from src/p0097.c -> libs/lib_p0097.so
_c_lib = import_c_lib('lib_p0097')

# Bind C function
_c_func = getattr(_c_lib, 'large_non_mersenne_prime')
_c_func.argtypes = [ctypes.c_int, ctypes.c_char_p]
_c_func.restype = ctypes.c_longlong


def _to_bytes(s: str) -> bytes:
    if not isinstance(s, str):
        raise TypeError('prime must be a string')
    return s.encode('utf-8')


def large_non_mersenne_prime(*, num_digits: int, prime: str) -> int:
    if not isinstance(num_digits, int) or num_digits <= 0:
        raise ValueError('num_digits must be a positive integer')
    return int(_c_func(int(num_digits), _to_bytes(prime)))
