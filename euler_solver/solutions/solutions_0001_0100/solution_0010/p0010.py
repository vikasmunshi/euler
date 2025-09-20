#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 10: Summation of Primes.

Problem Statement:
    The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.

    Find the sum of all the primes below two million.

Solution Approach:
    Use a prime sieve (e.g., Sieve of Eratosthenes) to efficiently find all primes below
    the given limit. Sum these primes. This approach runs in O(n log log n) time and uses
    O(n) space for the sieve.

Answer: 142913828922
URL: https://projecteuler.net/problem=10
"""
from __future__ import annotations

from typing import Any

import pyprimesieve as pps

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import (is_prime,
                                     primes_eratosthenes_sieve_upto_max_num,
                                     primes_generator,
                                     primes_sundaram_sieve)

euler_problem: int = 10
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_num': 10}, 'answer': 17},
    {'category': 'main', 'input': {'max_num': 2000000}, 'answer': 142913828922},
    {'category': 'extra', 'input': {'max_num': 10000000}, 'answer': 3203324994356},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_summation_of_primes_p0010_s0_eratosthenes_sieve(*, max_num: int) -> int:
    return sum(primes_eratosthenes_sieve_upto_max_num(max_num))


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_summation_of_primes_p0010_s1_sundaram_sieve(*, max_num: int) -> int:
    return sum(primes_sundaram_sieve(max_num))


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_summation_of_primes_p0010_s2_primes_generator(*, max_num: int) -> int:
    prime_number_gen = primes_generator()
    result: int = 0
    while (prime_number := next(prime_number_gen)) < max_num:
        result += prime_number
    return result


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_summation_of_primes_p0010_s3_is_prime(*, max_num: int) -> int:
    return sum(n for n in range(2, max_num) if is_prime(n))


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_summation_of_primes_p0010_s4_pps(*, max_num: int) -> int:
    return pps.primes_sum(max_num)  # type: ignore[no-any-return]


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
