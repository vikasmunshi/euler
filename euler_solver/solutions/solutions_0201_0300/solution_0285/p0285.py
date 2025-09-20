#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 285: Pythagorean Odds.

Problem Statement:
    Albert chooses a positive integer k, then two real numbers a and b are
    randomly chosen in the interval [0, 1] with uniform distribution.
    The square root of the sum (k * a + 1)^2 + (k * b + 1)^2 is computed and
    rounded to the nearest integer. If the result equals k, he scores k points;
    otherwise he scores nothing.

    For example, if k = 6, a = 0.2 and b = 0.85, then (k * a + 1)^2 + (k * b + 1)^2
    = 42.05. The square root is 6.484... which rounds to 6, so he scores 6
    points.

    It can be shown that if he plays 10 turns with k = 1, k = 2, ..., k = 10,
    the expected value of his total score, rounded to five decimal places, is
    10.20914.

    If he plays 10^5 turns with k = 1, k = 2, k = 3, ..., k = 10^5, what is the
    expected value of his total score, rounded to five decimal places?

URL: https://projecteuler.net/problem=285
"""
from typing import Any

euler_problem: int = 285
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_k': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_k': 100000}, 'answer': None},
    {'category': 'extra', 'input': {'max_k': 200000}, 'answer': None},
]
encrypted: str = (
    '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'
    'g3nKZsJw4ptnZDMG65+fFQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
