#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 73: Counting Fractions in a Range.

Problem Statement:
    Consider the fraction, n/d, where n and d are positive integers. If n < d and
    HCF(n, d) = 1, it is called a reduced proper fraction.

    If we list the set of reduced proper fractions for d ≤ 8 in ascending order of
    size, we get:
    1/8, 1/7, 1/6, 1/5, 1/4, 2/7, 1/3, 3/8, 2/5, 3/7, 1/2, 4/7, 3/5, 5/8, 2/3,
    5/7, 3/4, 4/5, 5/6, 6/7, 7/8

    It can be seen that there are 3 fractions between 1/3 and 1/2.

    How many fractions lie between 1/3 and 1/2 in the sorted set of reduced proper
    fractions for d ≤ 12000?

Solution Approach:
    Use number theory and Farey sequences or Euler's totient function techniques.
    Efficient counting can be done by recursively counting fractions in the range
    using mediant property or by leveraging the Farey sequence properties.
    Complexity is primarily determined by efficient gcd calculations and careful
    interval counting within given denominator constraints.

Answer: 7295372
URL: https://projecteuler.net/problem=73
"""
from __future__ import annotations

from typing import Any, List

from euler_solver.framework import evaluate, logger, register_solution, set_resource_limits

euler_problem: int = 73
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_d': 8}, 'answer': 3},
    {'category': 'dev', 'input': {'max_d': 1000}, 'answer': 50695},
    {'category': 'main', 'input': {'max_d': 12000}, 'answer': 7295372},
    {'category': 'extra', 'input': {'max_d': 100000}, 'answer': 506608484},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=2)
def solve_counting_fractions_in_a_range_p0073_s0(*, max_d: int) -> int:
    lower_denominator: int = 3
    upper_denominator: int = 2
    d = upper_denominator + lower_denominator * ((max_d - upper_denominator) // lower_denominator)
    prev_d = lower_denominator
    count = 0
    while d != upper_denominator:
        count += 1
        prev_d, d = (d, max_d - (max_d + prev_d) % d)
    return count


@register_solution(euler_problem=euler_problem, max_test_case_index=2)
@set_resource_limits(recursion_var='max_d', multiplier=1, set_int_max_str=False, when='always')
def solve_counting_fractions_in_a_range_p0073_s1(*, max_d: int) -> int:
    def recursion(lower_denominator: int, upper_denominator: int) -> int:
        if (mediant := (lower_denominator + upper_denominator)) > max_d:
            return 0
        return 1 + recursion(lower_denominator, mediant) + recursion(mediant, upper_denominator)

    return recursion(lower_denominator=3, upper_denominator=2)


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_counting_fractions_in_a_range_p0073_s2(*, max_d: int) -> int:
    def rank(n: int, d: int) -> int:
        len_data: int = max_d + 1
        data: List[int] = [i * n // d for i in range(len_data)]
        for i in range(1, len_data):
            for j in range(2 * i, len_data, i):
                data[j] -= data[i]
        return sum(data)

    return rank(n=1, d=2) - rank(n=1, d=3) - 1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
