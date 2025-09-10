#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 642: Sum of Largest Prime Factors.

Problem Statement:
    Let f(n) be the largest prime factor of n and F(n) = sum of f(i) for i from 2 to n.
    For example F(10)=32, F(100)=1915 and F(10000)=10118280.

    Find F(201820182018). Give your answer modulus 10^9.

Solution Approach:
    Use number theory to efficiently determine largest prime factors for large ranges.
    Employ segmented sieve or similar factorization optimizations to handle very large n.
    Accumulate sums modulo 10^9 to maintain manageable numeric limits.
    Expected complexity depends on optimization but sieve-based approaches and prime
    factor caching are typical avenues.

Answer: ...
URL: https://projecteuler.net/problem=642
"""
from __future__ import annotations

from math import isqrt
from typing import Any

import numpy as np
import pyprimesieve as pps

from euler_solver.c_libs import use_wrapped_c_function
from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 642
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num': 10}},
    {'category': 'dev', 'input': {'num': 100}},
    {'category': 'dev', 'input': {'num': 10_000}},
    {'category': 'dev', 'input': {'num': 100_000}},
    {'category': 'dev', 'input': {'num': 1_000_000}},
    {'category': 'dev', 'input': {'num': 10_000_000}},
    {'category': 'main', 'input': {'num': 201_820_182_018}},
]


def euler642_helper_1(n: int, sqrt_n: int, primes_list: list[int], modulo: int) -> int: ...

def euler642_helper_2(n: int, sqrt_n: int, primes_list: list[int], modulo: int) -> int: ...

@use_wrapped_c_function('p0642')
def euler642(n: int, modulo: int) -> int: ...

@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_sum_of_largest_prime_factors_p0642_s1_c(*, num: int) -> int: ...

@register_solution(euler_problem=euler_problem, max_test_case_index=4, allow_max_override=False)
def solve_sum_of_largest_prime_factors_p0642_s1_lpf_sieve(*, num: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
