#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 21: Amicable Numbers.

Problem Statement:
    Let d(n) be defined as the sum of proper divisors of n (numbers less than n which
    divide evenly into n).
    If d(a) = b and d(b) = a, where a ≠ b, then a and b are an amicable pair and each
    of a and b are called amicable numbers.

    For example, the proper divisors of 220 are 1, 2, 4, 5, 10, 11, 20, 22, 44, 55 and
    110; therefore d(220) = 284. The proper divisors of 284 are 1, 2, 4, 71 and 142; so
    d(284) = 220.

    Evaluate the sum of all the amicable numbers under 10000.

Solution Approach:
    Efficiently compute sum of proper divisors for all numbers up to the limit using
    a sieve-like method (number theory). Then identify amicable pairs by checking pairs
    a, b where d(a)=b and d(b)=a with a != b. Sum all such numbers. Expect O(n log n)
    complexity with careful divisor summation.

Answer: 31626
URL: https://projecteuler.net/problem=21
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 21
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_num': 10000}, 'answer': 31626},
]


@lru_cache()
def sum_factors(n: int) -> int:
    n_sqrt = int(n ** 0.5)
    return 1 + sum((i + n // i for i in range(2, n_sqrt + 1) if n % i == 0)) - (n_sqrt if n_sqrt ** 2 == n else 0)


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_amicable_numbers_p0021_s0(*, max_num: int) -> int:
    return sum((x for x in range(2, max_num + 1) if (y := sum_factors(x)) != x and sum_factors(y) == x))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
