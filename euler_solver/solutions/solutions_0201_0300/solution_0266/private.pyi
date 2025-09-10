#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 266: Pseudo Square Root.

Problem Statement:
    The divisors of 12 are: 1, 2, 3, 4, 6 and 12.
    The largest divisor of 12 that does not exceed the square root of 12 is 3.
    We shall call the largest divisor of an integer n that does not exceed the
    square root of n the pseudo square root (PSR) of n.
    It can be seen that PSR(3102) = 47.

    Let p be the product of the primes below 190.
    Find PSR(p) mod 10^16.

Solution Approach:
    Key ideas: number theory, prime products, subset-product (knapsack), meet-in-
    the-middle or DP on logarithms to find the largest divisor <= sqrt(n).
    For squarefree p (product of distinct primes) PSR(p) is the maximal subset
    product not exceeding sqrt(p). Use meet-in-the-middle: enumerate products
    of each half, sort and combine to find best product <= sqrt(p). Work in
    high-precision integers and reduce final answer modulo 10^16.
    Expected complexity: O(2^(n/2) log(2^(n/2))) time, O(2^(n/2)) memory for n primes.

Answer: ...
URL: https://projecteuler.net/problem=266
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 266
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 190}},
    {'category': 'extra', 'input': {'max_limit': 1000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_pseudo_square_root_p0266_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))