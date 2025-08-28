#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Python wrapper for C implementations of functions used in Project Euler problem 14. """
from __future__ import annotations

import contextlib
import ctypes
import sys

from euler_solver.c_libs import import_c_lib

MAX_VALID_INPUT = sys.maxsize

# Load the shared library built from src/p0014.c -> libs/lib_p0014.so
_c_lib = import_c_lib('lib_p0014')

# Resolve the C function symbols and set ctypes signatures
_c_collatz_len = _c_lib.collatz_sequence_length
_c_collatz_len.argtypes = [ctypes.c_longlong]
_c_collatz_len.restype = ctypes.c_longlong
_c_ensure_cache = _c_lib.ensure_cache
_c_ensure_cache.argtypes = []
_c_ensure_cache.restype = None
_c_free_cache = _c_lib.free_cache
_c_free_cache.argtypes = []
_c_free_cache.restype = None


@contextlib.contextmanager
def collatz_cache_context():
    try:
        _c_ensure_cache()
        yield collatz_sequence_length
    finally:
        _c_free_cache()


def collatz_sequence_length(number: int) -> int:
    """CTypes-backed Collatz sequence length with context-managed cache.

    Mirrors the Python signature used in solution_0014.solution.collatz_sequence_length.
    Accepts a positive integer and returns the count of terms ending at 1.
    """
    if not (0 < number < MAX_VALID_INPUT):
        raise ValueError(f'number must be between 0 and {MAX_VALID_INPUT}')
    n = ctypes.c_longlong(number)
    result: ctypes.c_longlong = _c_collatz_len(n)
    return int(result)
