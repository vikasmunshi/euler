#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" C library for prime number generation and testing """
from __future__ import annotations

import contextlib
import ctypes
import pathlib
import typing

__all__ = []

ERROR_MEMORY_ALLOCATION = -1
UINT64_MAX = 2 ** 64 - 1


def import_c_lib() -> ctypes.CDLL:
    c_path: pathlib.Path = pathlib.Path(__file__).parent / 'primes.c'
    lib_path: pathlib.Path = pathlib.Path(__file__).parent / 'lib_primes.so'
    if not lib_path.exists():
        from euler_solver.framework.loader import build_c_lib
        build_c_lib(c_path=c_path, lib_path=lib_path)
    try:
        # Load with RTLD_GLOBAL to allow symbol resolution across shared libs
        mode = getattr(ctypes, 'RTLD_GLOBAL', None)
        lib = ctypes.CDLL(lib_path.as_posix(), mode=mode) if mode is not None else ctypes.CDLL(lib_path.as_posix())
        return lib
    except OSError as e:
        raise ImportError(f'Failed to load C library {lib_path}. '
                          f'Make sure the library is compiled and installed correctly: {e}')


# Import the C functions
c_lib = import_c_lib()

# C is_prime binding
_is_prime_c = c_lib.is_prime
_is_prime_c.argtypes = [ctypes.c_uint64]
_is_prime_c.restype = ctypes.c_bool


def is_prime(num: int) -> bool:
    if not 0 <= num <= UINT64_MAX:
        raise ValueError(f"Number must be between 0 and {UINT64_MAX}")
    return bool(_is_prime_c(ctypes.c_uint64(num)))


__all__.append('is_prime')

# C fast_is_prime binding
_fast_is_prime_c = c_lib.fast_is_prime
_fast_is_prime_c.argtypes = [ctypes.c_uint64]
_fast_is_prime_c.restype = ctypes.c_bool


def fast_is_prime(num: int) -> bool:
    if not 0 <= num <= UINT64_MAX:
        raise ValueError(f"Number must be between 0 and {UINT64_MAX}")
    return bool(_fast_is_prime_c(ctypes.c_uint64(num)))


__all__.append('fast_is_prime')

# C primes_sundaram_sieve bindings
_primes_sundaram_sieve_c = c_lib.primes_sundaram_sieve
_primes_sundaram_sieve_c.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64)]
_primes_sundaram_sieve_c.restype = ctypes.c_int


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    if not 0 <= max_num <= UINT64_MAX:
        raise ValueError(f"Number must be between 0 and {UINT64_MAX}")
    if max_num < 2:
        return tuple()
    max_num_ctypes = ctypes.c_uint64(max_num)
    array_size = (max_num // 2) + 1  # Sundaram sieve needs n/2 + 1 space
    primes_out = (ctypes.c_uint64 * array_size)()
    result = _primes_sundaram_sieve_c(max_num_ctypes, primes_out)
    if result == ERROR_MEMORY_ALLOCATION:
        raise MemoryError("Memory allocation error in primes_sundaram_sieve_c")
    elif result < 0:  # Catch otherwise unspecified errors
        raise RuntimeError("An unexpected error occurred in the C library")
    return tuple(int(primes_out[i]) for i in range(result))


__all__.append('primes_sundaram_sieve')

# C primes_eratosthenes_sieve bindings
_primes_eratosthenes_sieve_c = c_lib.primes_eratosthenes_sieve
_primes_eratosthenes_sieve_c.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64)]
_primes_eratosthenes_sieve_c.restype = ctypes.c_int


def primes_eratosthenes_sieve_upto_max_num(max_num: int) -> tuple[int, ...]:
    if not 0 <= max_num <= UINT64_MAX:
        raise ValueError(f"Number must be between 0 and {UINT64_MAX}")
    if max_num < 2:
        return tuple()
    max_num_ctypes = ctypes.c_uint64(max_num)
    array_size = max_num // 2  # Eratosthenes sieve needs n/2 space
    primes_out = (ctypes.c_uint64 * array_size)()
    result = _primes_eratosthenes_sieve_c(max_num_ctypes, primes_out)
    if result == ERROR_MEMORY_ALLOCATION:
        raise MemoryError("Memory allocation error in primes_eratosthenes_sieve_c")
    elif result < 0:  # Catch otherwise unspecified errors
        raise RuntimeError("An unexpected error occurred in the C library")
    return tuple(int(primes_out[i]) for i in range(result))


__all__.append('primes_eratosthenes_sieve_upto_max_num')

# Indefinite prime generator via C stateful API
_primes_generator_init_c = c_lib.primes_generator_init
_primes_generator_init_c.argtypes = []
_primes_generator_init_c.restype = ctypes.c_void_p

_primes_generator_next_c = c_lib.primes_generator_next
_primes_generator_next_c.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64)]
_primes_generator_next_c.restype = ctypes.c_bool

_primes_generator_free_c = c_lib.primes_generator_free
_primes_generator_free_c.argtypes = [ctypes.c_void_p]
_primes_generator_free_c.restype = None


@contextlib.contextmanager
def _state() -> typing.Generator[ctypes.c_void_p, None, None]:
    internal_state = _primes_generator_init_c()
    if not internal_state:
        raise MemoryError("Failed to allocate C state for prime generator")
    try:
        yield internal_state
    finally:
        _primes_generator_free_c(internal_state)


def primes_generator() -> typing.Generator[int, None, None]:
    """Yield primes indefinitely using C-backed generator state.

    This wraps a stateful C generator. Memory is always released via a
    context-managed finalizer even if the consumer stops early.
    """
    with _state() as state:
        out_val = ctypes.c_uint64()
        while True:
            ok = _primes_generator_next_c(state, ctypes.byref(out_val))
            if not ok:
                return  # gracefully end if C cannot produce further primes
            yield int(out_val.value)


__all__.append('primes_generator')

# C count_divisors_square binding
_count_divisors_square_c = c_lib.count_divisors_square
_count_divisors_square_c.argtypes = [ctypes.c_uint64]
_count_divisors_square_c.restype = ctypes.c_uint64


def count_divisors_square(n: int) -> int:
    """Count the number of divisors of n^2 using prime factorization."""
    if not 0 <= n <= UINT64_MAX:
        raise ValueError(f"Number must be between 0 and {UINT64_MAX}")
    return int(_count_divisors_square_c(ctypes.c_uint64(n)))


__all__ = [*__all__, 'count_divisors_square']

# C num_factors binding
_num_factors_c = c_lib.num_factors
_num_factors_c.argtypes = [ctypes.c_uint64]
_num_factors_c.restype = ctypes.c_uint64


def num_factors(n: int) -> int:
    """Count the number of divisors for a given number using trial division (C implementation).

    For n == 0, returns 0 to avoid undefined behavior.
    """
    if not 0 <= n <= UINT64_MAX:
        raise ValueError(f"Number must be between 0 and {UINT64_MAX}")
    return int(_num_factors_c(ctypes.c_uint64(n)))


__all__ = [*__all__, 'num_factors']

# C sum_proper_divisors binding
_sum_proper_divisors_c = c_lib.sum_proper_divisors
_sum_proper_divisors_c.argtypes = [ctypes.c_uint64]
_sum_proper_divisors_c.restype = ctypes.c_uint64


def sum_proper_divisors(n: int) -> int:
    """Calculate the sum of proper divisors of n (C implementation).

    Mirrors maths.primes.sum_proper_divisors reference implementation.
    """
    if not 0 <= n <= UINT64_MAX:
        raise ValueError(f"Number must be between 0 and {UINT64_MAX}")
    return int(_sum_proper_divisors_c(ctypes.c_uint64(n)))


__all__ = [*__all__, 'sum_proper_divisors']

# C prime_factor_count binding
_prime_factor_count_c = c_lib.prime_factor_count
_prime_factor_count_c.argtypes = [ctypes.c_uint64]
_prime_factor_count_c.restype = ctypes.c_uint64


def prime_factor_count(n: int) -> int:
    """Count the number of unique prime factors of a number (C implementation).

    Mirrors maths.primes.prime_factor_count reference implementation.
    """
    if not 0 <= n <= UINT64_MAX:
        raise ValueError(f"Number must be between 0 and {UINT64_MAX}")
    return int(_prime_factor_count_c(ctypes.c_uint64(n)))


__all__ = [*__all__, 'prime_factor_count']

# C prime_factorization binding
_ERROR_INSUFFICIENT_BUFFER = -2
_prime_factorization_c = c_lib.prime_factorization
_prime_factorization_c.argtypes = [
    ctypes.c_uint64,
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_size_t,
]
_prime_factorization_c.restype = ctypes.c_int


def prime_factorization(n: int) -> tuple[tuple[int, int], ...]:
    """Prime factorization using the C implementation.

    Returns a tuple of (base, exponent) pairs sorted by increasing base.
    For n <= 1, returns an empty tuple.
    """
    if not 0 <= n <= UINT64_MAX:
        raise ValueError(f"Number must be between 0 and {UINT64_MAX}")
    if n <= 1:
        return tuple()
    capacity = 1024
    bases_buf = (ctypes.c_uint64 * capacity)()
    exps_buf = (ctypes.c_uint32 * capacity)()
    count = _prime_factorization_c(ctypes.c_uint64(n), bases_buf, exps_buf, ctypes.c_size_t(capacity))
    if count == ERROR_MEMORY_ALLOCATION:
        raise MemoryError("Memory allocation error in C prime_factorization")
    if count == _ERROR_INSUFFICIENT_BUFFER:
        # extremely defensive cap; 64-bit numbers won't need this
        raise RuntimeError("Prime factorization buffer growth exceeded safe limit")
    if count < 0:
        raise RuntimeError("Unexpected error from C prime_factorization")
    return tuple((int(bases_buf[i]), int(exps_buf[i])) for i in range(count))


__all__ = [*__all__, 'prime_factorization']
