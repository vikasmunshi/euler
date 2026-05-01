#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 77: Prime Summations.

Problem Statement:
    It is possible to write ten as the sum of primes in exactly five different ways:
    7 + 3
    5 + 5
    5 + 3 + 2
    3 + 3 + 2 + 2
    2 + 2 + 2 + 2 + 2

    What is the first value which can be written as the sum of primes in over five
    thousand different ways?

Solution Approach:
    Use dynamic programming to count partitions of integers into prime summands.
    Generate primes up to a suitable limit using a sieve. The count for each number
    can be computed from smaller numbers by adding primes recursively.
    The first integer with count > 5000 is the answer.
    Time complexity depends on the upper bound for search; DP with prime sieve is efficient.

Answer: 71
URL: https://projecteuler.net/problem=77
"""
from __future__ import annotations

from functools import lru_cache
from itertools import count
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import primes_sundaram_sieve

euler_problem: int = 77
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_prime_partitions': 5}, 'answer': 10},
    {'category': 'dev', 'input': {'num_prime_partitions': 50}, 'answer': 25},
    {'category': 'dev', 'input': {'num_prime_partitions': 500}, 'answer': 45},
    {'category': 'main', 'input': {'num_prime_partitions': 5000}, 'answer': 71},
    {'category': 'extra', 'input': {'num_prime_partitions': 50000}, 'answer': 104},
]


@lru_cache(maxsize=None)
def num_prime_partitions_simple_recursion(*, number: int, slots: int) -> int:
    if number < 0 or slots < 0:
        raise ValueError('number and slots must be non-negative')
    if number == 0:
        return 1
    if slots < 2:  # 2 is the smallest prime
        return 0
    result = 0
    max_num = min(number, slots)
    for n in primes_sundaram_sieve(max_num):
        result += num_prime_partitions_simple_recursion(number=number - n, slots=n)
    return result


@lru_cache(maxsize=None)
def get_prime_partitions_simple_recursion(*, number: int, slots: int, safe_limit: int | None = 50) -> list[list[int]]:
    if safe_limit and number > safe_limit:
        raise OverflowError(f'number must be less than {safe_limit=}')
    if number < 0 or slots < 0:
        raise ValueError('number and slots must be non-negative')
    if number < 2 or slots < 2:  # 2 is the smallest prime
        return []
    prime_partitions: list[list[int]] = []
    max_num = min(number, slots)
    for n in primes_sundaram_sieve(max_num):
        if n == number:
            prime_partitions.append([n])
        else:
            for partition in get_prime_partitions_simple_recursion(number=number - n, slots=min(number - n, n),
                                                                   safe_limit=safe_limit):
                prime_partitions.append([n] + partition)
    for partition in prime_partitions:
        assert sum(partition) == number, f'{partition=} {sum(partition)=} {number=}'
    return prime_partitions


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_summations_p0077_s0(*, num_prime_partitions: int) -> int:
    for n in count(1):
        if num_prime_partitions_simple_recursion(number=n, slots=n) >= num_prime_partitions:
            return n
    return -1


@register_solution(euler_problem=euler_problem, max_test_case_index=0, allow_max_override=False)
def solve_prime_summations_p0077_s1(*, num_prime_partitions: int) -> int:
    for n in count(2):
        if len(get_prime_partitions_simple_recursion(number=n, slots=n)) >= num_prime_partitions:
            return n
    return -1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
