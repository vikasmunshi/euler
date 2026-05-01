#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 87: Prime Power Triples.

Problem Statement:
    The smallest number expressible as the sum of a prime square, prime cube, and
    prime fourth power is 28. In fact, there are exactly four numbers below fifty
    that can be expressed in such a way:

        28 = 2^2 + 2^3 + 2^4
        33 = 3^2 + 2^3 + 2^4
        49 = 5^2 + 2^3 + 2^4
        47 = 2^2 + 3^3 + 2^4

    How many numbers below fifty million can be expressed as the sum of a prime
    square, prime cube, and prime fourth power?

Solution Approach:
    Use sieve of Eratosthenes to generate primes up to roughly sqrt(50 million).
    Enumerate sums of prime^2 + prime^3 + prime^4 below 50 million.
    Use sets for quick uniqueness and containment.
    This approach is efficient with optimized prime generation and pruning.

Answer: 1097343
URL: https://projecteuler.net/problem=87
"""
from __future__ import annotations

from math import sqrt
from typing import Any, Generator, Tuple

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import primes_sundaram_sieve

euler_problem: int = 87
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_num': 50}, 'answer': 4},
    {'category': 'main', 'input': {'max_num': 50000000}, 'answer': 1097343},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_power_triples_p0087_s0(*, max_num: int) -> int:
    primes: Tuple[int, ...] = primes_sundaram_sieve(int(sqrt(max_num)))
    numbers = set()
    max_quadruple_cube: int = max_num - 4
    max_quadruple: int = max_quadruple_cube - 8
    for quadruple in prime_powers(primes, 4):
        if quadruple > max_quadruple:
            break
        for cube in prime_powers(primes, 3):
            if (quadruple_cube := (quadruple + cube)) > max_quadruple_cube:
                break
            for square in prime_powers(primes, 2):
                if (number := (quadruple_cube + square)) >= max_num:
                    break
                numbers.add(number)
    return len(numbers)


def prime_powers(primes: Tuple[int, ...], exponent: int) -> Generator[int, None, None]:
    for base in primes:
        yield base ** exponent


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
