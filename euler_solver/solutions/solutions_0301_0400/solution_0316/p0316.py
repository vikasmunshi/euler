#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 316: Numbers in Decimal Expansions.

Problem Statement:
    Let p = p_1 p_2 p_3 ... be an infinite sequence of random digits,
    selected from {0,1,2,3,4,5,6,7,8,9} with equal probability.
    It can be seen that p corresponds to the real number 0.p_1 p_2 p_3 ...
    It can also be seen that choosing a random real number from [0,1) is
    equivalent to choosing an infinite sequence of random digits
    selected from {0,1,2,3,4,5,6,7,8,9} with equal probability.

    For any positive integer n with d decimal digits, let k be the smallest
    index such that p_k, p_{k + 1}, ..., p_{k + d - 1} are the decimal
    digits of n, in the same order.
    Also, let g(n) be the expected value of k; it can be proven that g(n)
    is always finite and, interestingly, always an integer number.

    For example, if n = 535, then
    for p = 31415926 535 897..., we get k = 9
    for p = 35528714365004956000049084876408468 535 4..., we get k = 36
    etc and we find that g(535) = 1008.

    Given that sum_{n = 2}^{999} g(floor(10^6 / n)) = 27280188, find
    sum_{n = 2}^{999999} g(floor(10^16 / n)).

URL: https://projecteuler.net/problem=316
"""
from typing import Any

euler_problem: int = 316
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n_max': 10, 'ten_power': 6}, 'answer': None},
    {'category': 'main', 'input': {'n_max': 999999, 'ten_power': 16}, 'answer': None},
]
encrypted: str = (
    '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'
    '2aj8fjQv8WEt2YlJaRwNo4F8FR3pGvz5'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
