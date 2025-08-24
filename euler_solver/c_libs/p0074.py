#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Python wrapper for C implementations of functions used in Project Euler problem 74. """
from __future__ import annotations

import ctypes
import sys
from collections import namedtuple

from euler_solver.c_libs.import_c_lib import import_c_lib

__all__ = ['count_digit_factorial_max_length_chains_c']

ERROR_NULL_OUTPUT_PTRS = 1
ERROR_MEMORY_ALLOCATION_CACHE = 2
ERROR_MEMORY_ALLOCATION_SEEN = 3
ERROR_MEMORY_REALLOCATION_SEEN = 4
MAX_VALID_INPUT = sys.maxsize  # for numbers with more than 7 digits, sum of digit factorials is less than the number.


# Exception class for error handling
class DigitFactorialError(RuntimeError):
    pass


# Import the C function
try:
    c_func = import_c_lib('lib_p0074', 'count_digit_factorial_max_length_chains')
    c_func.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
    c_func.restype = ctypes.c_int
except OSError as e:
    raise ImportError("Failed to import C library 'lib_p0074': " + str(e))

# Named tuple for clearer return values
Result = namedtuple('Result', ['max_chain_length', 'max_chain_count'])


def count_digit_factorial_max_length_chains_c(max_num: int) -> Result:
    """
    Compute the longest and most frequent digit factorial chain for numbers up to max_num.

    Args:
        max_num (int): The maximum number to consider when calculating digit factorial chains.

    Returns:
        Result: Named tuple containing:
            - max_chain_length (int): The longest chain length.
            - max_chain_count (int): Count of numbers with the longest chain length.

    Raises:
        ValueError: If max_num is outside the valid range.
        DigitFactorialError: If an error occurs in the underlying C function.
    """
    if not (0 <= max_num <= MAX_VALID_INPUT):
        raise ValueError(f'max_num must be between 0 and {MAX_VALID_INPUT}')
    max_num = ctypes.c_int(max_num)
    chain_count = ctypes.c_int()
    max_length = ctypes.c_int()
    result = c_func(max_num, ctypes.byref(chain_count), ctypes.byref(max_length))

    if result != 0:
        error_messages = {
            ERROR_NULL_OUTPUT_PTRS: "Null output pointers provided",
            ERROR_MEMORY_ALLOCATION_CACHE: "Failed to allocate memory for cache",
            ERROR_MEMORY_ALLOCATION_SEEN: "Failed to allocate memory for seen array",
            ERROR_MEMORY_REALLOCATION_SEEN: "Failed to reallocate memory for seen array"
        }
        error_message = error_messages.get(result, f"Unknown error code: {result}")
        raise DigitFactorialError(
                f'Error in C function: {error_message} (max_num={max_num.value})'
        )

    return Result(chain_count.value, max_length.value)
