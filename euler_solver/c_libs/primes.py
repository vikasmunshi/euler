#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" C library for prime number generation and testing """
from __future__ import annotations

import ctypes

from euler_solver.c_libs import import_c_lib

ERROR_MEMORY_ALLOCATION = -1
UINT64_MAX = 2 ** 64 - 1

# Import the C functions
c_lib = import_c_lib('lib_primes')

is_prime_c = c_lib.is_prime
is_prime_c.argtypes = [ctypes.c_uint64]
is_prime_c.restype = ctypes.c_bool


def is_prime(num: int) -> bool:
    if not 0 <= num <= UINT64_MAX:
        raise ValueError(f"Number must be between 0 and {UINT64_MAX}")
    num = ctypes.c_uint64(num)
    result = is_prime_c(num)
    return result


primes_sundaram_sieve_c = c_lib.primes_sundaram_sieve
primes_sundaram_sieve_c.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64)]
primes_sundaram_sieve_c.restype = ctypes.c_int


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    if not 0 <= max_num <= UINT64_MAX:
        raise ValueError(f"Number must be between 0 and {UINT64_MAX}")
    if max_num < 2:
        return tuple()
    max_num_ctypes = ctypes.c_uint64(max_num)
    array_size = (max_num // 2) + 1  # Sundaram sieve needs n/2 + 1 space
    primes_out = (ctypes.c_uint64 * array_size)()
    result = primes_sundaram_sieve_c(max_num_ctypes, primes_out)
    if result == ERROR_MEMORY_ALLOCATION:
        raise MemoryError("Memory allocation error in primes_sundaram_sieve_c")
    elif result < 0:  # Catch otherwise unspecified errors
        raise RuntimeError("An unexpected error occurred in the C library")
    return tuple(int(primes_out[i]) for i in range(result))


primes_eratosthenes_sieve_c = c_lib.primes_eratosthenes_sieve
primes_eratosthenes_sieve_c.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64)]
primes_eratosthenes_sieve_c.restype = ctypes.c_int


def primes_eratosthenes_sieve(max_num: int) -> tuple[int, ...]:
    if not 0 <= max_num <= UINT64_MAX:
        raise ValueError(f"Number must be between 0 and {UINT64_MAX}")
    if max_num < 2:
        return tuple()
    max_num_ctypes = ctypes.c_uint64(max_num)
    array_size = max_num // 2  # Eratosthenes sieve needs n/2 space
    primes_out = (ctypes.c_uint64 * array_size)()
    result = primes_eratosthenes_sieve_c(max_num_ctypes, primes_out)
    if result == ERROR_MEMORY_ALLOCATION:
        raise MemoryError("Memory allocation error in primes_eratosthenes_sieve_c")
    elif result < 0:  # Catch otherwise unspecified errors
        raise RuntimeError("An unexpected error occurred in the C library")
    return tuple(int(primes_out[i]) for i in range(result))
