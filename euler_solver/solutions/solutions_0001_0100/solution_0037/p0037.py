#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 37: Truncatable Primes.

Problem Statement:
    The number 3797 has an interesting property. Being prime itself, it is possible
    to continuously remove digits from left to right, and remain prime at each stage:
    3797, 797, 97, and 7. Similarly we can work from right to left: 3797, 379, 37,
    and 3.

    Find the sum of the only eleven primes that are both truncatable from left to
    right and right to left.

    NOTE: 2, 3, 5, and 7 are not considered to be truncatable primes.

Solution Approach:
    Use prime checking and truncation checks for both left and right digit removal.
    Efficient primality tests and caching found primes can improve performance.
    Brute force search with pruning is feasible due to the rarity of truncatable primes.

Answer: 748317
URL: https://projecteuler.net/problem=37
"""
from __future__ import annotations

from typing import Any, List, Set

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import primes_generator

euler_problem: int = 37
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': 748317},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_truncatable_primes_p0037_s0() -> int:
    primes: Set[str] = set()
    truncatable_primes: List[int] = list()
    for prime_num in primes_generator():
        prime = str(prime_num)
        primes.add(prime)
        if int(prime) < 10:
            continue
        if not any((pl not in primes or pr not in primes
                    for pl, pr in [(prime[i:], prime[:i]) for i in range(1, len(prime))])):
            truncatable_primes.append(prime_num)
        if len(truncatable_primes) == 11:
            break
    return sum(truncatable_primes)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
