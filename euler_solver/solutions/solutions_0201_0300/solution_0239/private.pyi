#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 239: Twenty-two Foolish Primes.

Problem Statement:
    A set of disks numbered 1 through 100 are placed in a line in random order.

    What is the probability that we have a partial derangement such that
    exactly 22 prime number discs are found away from their natural positions?
    (Any number of non-prime disks may also be found in or out of their natural
    positions.)

    Give your answer rounded to 12 places behind the decimal point in the form
    0.abcdefghijkl.

Solution Approach:
    Count primes in 1..100 (there are 25). Choose which 3 primes remain fixed
    (C(25,3)) so the other 22 primes must be displaced. Use inclusion–exclusion
    to count permutations of the remaining 97 elements where a specified set
    of m=22 elements have no fixed points:
        count = sum_{k=0..m} (-1)^k * C(m,k) * (97-k)!
    Probability = C(25,3) * count / 100!.
    Key ideas: combinatorics, inclusion–exclusion, factorials and binomial coeffs.
    Complexity: O(m) arithmetic with factorials up to 100 (feasible with Python
    big integers).

Answer: ...
URL: https://projecteuler.net/problem=239
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 239
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_twenty_two_foolish_primes_p0239_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))