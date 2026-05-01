#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 35: Circular Primes.

Problem Statement:
    The number, 197, is called a circular prime because all rotations of the digits:
    197, 971, and 719, are themselves prime.

    There are thirteen such primes below 100: 2, 3, 5, 7, 11, 13, 17, 31, 37, 71,
    73, 79, and 97.

    How many circular primes are there below one million?

Solution Approach:
    Use number theory and prime checking with a sieve (e.g., Sieve of Eratosthenes)
    to identify primes below one million. For each prime, generate all digit rotations
    and verify all are prime. Count those where all rotations are prime.

Answer: 55
URL: https://projecteuler.net/problem=35
"""
from __future__ import annotations

from typing import Any, Set

import pyprimesieve as pps

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import primes_sundaram_sieve

euler_problem: int = 35
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': 4},
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': 13},
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': 25},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': 55},
    {'category': 'extra', 'input': {'max_limit': 10000000}, 'answer': 55},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_circular_primes_p0035_s0(*, max_limit: int) -> int:
    primes = set(primes_sundaram_sieve(max_limit))
    circular_primes = [prime for prime in primes
                       if prime < 10
                       or (not any((d in str(prime) for d in '024568'))
                           and (not any((rotated_number not in primes
                                         for rotated_number in get_rotated_numbers(num=prime)))))]
    return len(circular_primes)


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_circular_primes_p0035_s1_pps(*, max_limit: int) -> int:
    primes = set(pps.primes(max_limit))
    circular_primes = [prime for prime in primes
                       if prime < 10
                       or (not any((d in str(prime) for d in '024568'))
                           and (not any((rotated_number not in primes
                                         for rotated_number in get_rotated_numbers(num=prime)))))]
    return len(circular_primes)


def get_rotated_numbers(*, num: int) -> Set[int]:
    str_num: str = str(num)
    return {num} if len(str_num) == 1 else {int(str_num[i:] + str_num[:i]) for i in range(1, len(str_num) + 1)}


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
