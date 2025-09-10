#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python wrapper for C implementations used in Project Euler problem 112. """
from __future__ import annotations

import ctypes

from euler_solver.c_libs.wrapper import import_c_lib

__all__ = [
    'euler112',
]

# Load the C library built from src/p0112.c -> libs/lib_p0112.so
_c_lib = import_c_lib('lib_p0112')

# Bind C function
_c_func = getattr(_c_lib, 'euler112')
_c_func.argtypes = [ctypes.c_int]
_c_func.restype = ctypes.c_longlong


def euler112(target_percentage: int) -> int:
    if not (0 <= target_percentage <= 100):
        raise ValueError('target_percentage must be between 1 and 99')
    return int(_c_func(ctypes.c_int(target_percentage)))
