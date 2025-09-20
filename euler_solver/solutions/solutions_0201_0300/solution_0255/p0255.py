#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 255: Rounded Square Roots.

Problem Statement:
    We define the rounded-square-root of a positive integer n as the square root
    of n rounded to the nearest integer.

    The following procedure (essentially Heron's method adapted to integer
    arithmetic) finds the rounded-square-root of n:

    Let d be the number of digits of the number n.
    If d is odd, set x0 = 2 * 10^((d-1)/2).
    If d is even, set x0 = 7 * 10^((d-2)/2).
    Repeat:
    x_{k+1} = floor((x_k + ceil(n / x_k)) / 2)
    until x_{k+1} = x_k.

    Example: n = 4321 has 4 digits so x0 = 7 * 10^((4-2)/2) = 70.
    x1 = floor((70 + ceil(4321/70)) / 2) = 66
    x2 = floor((66 + ceil(4321/66)) / 2) = 66
    Since x2 = x1 we stop and the rounded-square-root is 66.

    The number of iterations required when using this method is surprisingly
    low. For example, a 5-digit integer (10000 <= n <= 99999) requires on
    average 3.2102888889 iterations (average rounded to 10 decimal places).

    Using the procedure described above, what is the average number of
    iterations required to find the rounded-square-root of a 14-digit number
    (10^13 <= n < 10^14)? Give your answer rounded to 10 decimal places.

URL: https://projecteuler.net/problem=255
"""
from typing import Any

euler_problem: int = 255
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'digits': 5}, 'answer': None},
    {'category': 'main', 'input': {'digits': 14}, 'answer': None},
    {'category': 'extra', 'input': {'digits': 16}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
