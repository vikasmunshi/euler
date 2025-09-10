#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 249: Prime Subset Sums.

Problem Statement:
    Let S = {2, 3, 5, ..., 4999} be the set of prime numbers less than 5000.
    Find the number of subsets of S, the sum of whose elements is a prime
    number.
    Enter the rightmost 16 digits as your answer.

Solution Approach:
    Use subset-sum generating functions: the coefficient of x^k in the product
    prod_{p in S} (1 + x^p) counts subsets summing to k. Compute coefficients
    efficiently with integer convolution (FFT/NTT) by multiplying polynomials
    for batches of primes or by divide-and-conquer convolution.
    Keep counts modulo 10^16 (rightmost 16 digits) throughout to limit size.
    Alternatively, direct DP over sums (dp[s]+=dp[s-p]) is simple but O(n*T)
    where T is total sum; convolution approaches reduce to roughly O(T log T).
    Memory is O(T) where T is the maximum achievable sum (sum of primes < limit).

Answer: ...
URL: https://projecteuler.net/problem=249
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 249
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 30}},
    {'category': 'main', 'input': {'max_limit': 5000}},
    {'category': 'extra', 'input': {'max_limit': 10000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_subset_sums_p0249_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))