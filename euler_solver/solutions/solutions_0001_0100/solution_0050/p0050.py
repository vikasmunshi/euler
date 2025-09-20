#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 50: Consecutive Prime Sum.

Problem Statement:
    The prime 41, can be written as the sum of six consecutive primes:
    41 = 2 + 3 + 5 + 7 + 11 + 13.
    This is the longest sum of consecutive primes that adds to a prime below
    one-hundred.

    The longest sum of consecutive primes below one-thousand that adds to a
    prime, contains 21 terms, and is equal to 953.

    Which prime, below one-million, can be written as the sum of the most
    consecutive primes?

Solution Approach:
    Use prime generation with a sieve (e.g., Sieve of Eratosthenes) up to the
    limit. Employ prefix sums for consecutive primes and check primality
    efficiently. A nested iteration over start and end indices with pruning
    will yield the longest consecutive prime sum. Expected complexity is near
    O(N log log N) for sieve plus O(N^2) in worst case for sums, reduced by
    pruning.

Answer: 997651
URL: https://projecteuler.net/problem=50
"""
from __future__ import annotations

from itertools import accumulate
from typing import Any, List, Set, Tuple

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import primes_sundaram_sieve

euler_problem: int = 50
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': 41},
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': 953},
    {'category': 'dev', 'input': {'max_limit': 10000}, 'answer': 9521},
    {'category': 'dev', 'input': {'max_limit': 100000}, 'answer': 92951},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': 997651},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_consecutive_prime_sum_p0050_s0(*, max_limit: int) -> int:
    primes_tuple: Tuple[int, ...] = primes_sundaram_sieve(max_limit)
    prime_sums: List[int] = [0] + list(accumulate(primes_tuple))
    primes: Set[int] = set(primes_tuple)
    number_of_primes_in_sum, prime = (0, 0)
    for i in range(number_of_primes_in_sum, len(prime_sums), 1):
        for j in range(i - number_of_primes_in_sum - 1, -1, -1):
            possible_prime = prime_sums[i] - prime_sums[j]
            if possible_prime > max_limit:
                break
            if possible_prime in primes:
                number_of_primes_in_sum = i - j
                prime = possible_prime
    return prime


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
