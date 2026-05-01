#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 97: Large Non-Mersenne Prime.

Problem Statement:
    The first known prime found to exceed one million digits was discovered in 1999,
    and is a Mersenne prime of the form 2^6972593 - 1; it contains exactly 2098960 digits.
    Subsequently other Mersenne primes, of the form 2^p - 1, have been found which contain
    more digits.

    However, in 2004 there was found a massive non-Mersenne prime which contains 2357207 digits:
    28433 * 2^7830457 + 1.

    Find the last ten digits of this prime number.

Solution Approach:
    Use modular arithmetic to compute (28433 * 2^7830457 + 1) mod 10^10 efficiently.
    Employ fast exponentiation (binary exponentiation) for O(log n) complexity in exponentiation.
    This avoids handling the entire large number outright.

Answer: 8739992577
URL: https://projecteuler.net/problem=97
"""
from __future__ import annotations

from ctypes import c_char_p, c_int, c_longlong
from typing import Any, Callable

from euler_solver.framework import evaluate, import_c_lib, logger, register_solution, use_c_function

euler_problem: int = 97
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'num_digits': 10, 'prime': '28433 × 2^7830457 + 1'}, 'answer': 8739992577},
]


def c_wrapper() -> tuple[Callable, ...]:
    # Load the C library built from src/p0097.c -> libs/lib_p0097.so
    _c_lib = import_c_lib(euler_problem)

    # Bind C function
    _c_func = getattr(_c_lib, 'large_non_mersenne_prime')
    _c_func.argtypes = [c_int, c_char_p]
    _c_func.restype = c_longlong

    def large_non_mersenne_prime_c(*, num_digits: int, prime: str) -> int:
        if not isinstance(num_digits, int) or num_digits <= 0:
            raise ValueError('num_digits must be a positive integer')
        return int(_c_func(int(num_digits), prime.encode('utf-8')))

    return (large_non_mersenne_prime_c,)


@use_c_function(c_wrapper, 0)
def large_non_mersenne_prime(*, num_digits: int, prime: str) -> int:
    divisor: int = 10 ** num_digits
    prime_parts: list[str] = prime.split()
    number: int
    exponent: int
    number, exponent = (int(prime_parts[0]), int(prime_parts[2][2:]))
    for _ in range(exponent):
        number *= 2
        number %= divisor
    number += 1
    number %= divisor
    return number


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_large_non_mersenne_prime_p0097_s0(*, num_digits: int, prime: str) -> int:
    return large_non_mersenne_prime(num_digits=num_digits, prime=prime)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
