#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 92: Square Digit Chains.

Problem Statement:
    A number chain is created by continuously adding the square of the digits in
    a number to form a new number until it has been seen before.

    For example,
        44 -> 32 -> 13 -> 10 -> 1 -> 1
        85 -> 89 -> 145 -> 42 -> 20 -> 4 -> 16 -> 37 -> 58 -> 89

    Therefore any chain that arrives at 1 or 89 will become stuck in an endless loop.
    What is most amazing is that EVERY starting number will eventually arrive at 1 or 89.

    How many starting numbers below ten million will arrive at 89?

Solution Approach:
    Use caching/memoization for chain ends to avoid recomputation.
    Generate chains by repeatedly summing the squares of digits.
    Count how many numbers below 10 million end at 89.
    Time complexity roughly O(N * d) where d is digit count, optimized by memoization.

Answer: 8581146
URL: https://projecteuler.net/problem=92
"""
from __future__ import annotations

from typing import Any, Dict

from euler_solver.framework import evaluate, logger, register_solution, show_solution

euler_problem: int = 92
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'power_of_10': 2}, 'answer': 80},
    {'category': 'dev', 'input': {'power_of_10': 3}, 'answer': 857},
    {'category': 'dev', 'input': {'power_of_10': 4}, 'answer': 8558},
    {'category': 'dev', 'input': {'power_of_10': 5}, 'answer': 85623},
    {'category': 'dev', 'input': {'power_of_10': 6}, 'answer': 856929},
    {'category': 'main', 'input': {'power_of_10': 7}, 'answer': 8581146},
    {'category': 'extra', 'input': {'power_of_10': 8}, 'answer': 85744333},
    {'category': 'extra', 'input': {'power_of_10': 9}, 'answer': 854325192},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_square_digit_chains_p0092_s0(*, power_of_10: int) -> int:
    a, sq, is89 = ([1], [x ** 2 for x in range(1, 10)], [False])
    results: Dict[int, int] = {}
    for n in range(1, power_of_10 + 1):
        b, a = (a, a + [0] * 81)
        is89 += map(terminates_in_89, range(len(b), len(a)))
        for i, v in enumerate(b):
            for s in sq:
                a[i + s] += v
        results[n] = sum((a[i] for i in range(len(a)) if is89[i]))
    if show_solution():
        print(f'Results for power_of_10={power_of_10}: {results}')
    return results[power_of_10]


def terminates_in_89(n: int) -> bool:
    while n != 1 and n != 89:
        n, t = (0, n)
        while t:
            n, t = (n + (t % 10) ** 2, t // 10)
    return n == 89


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
