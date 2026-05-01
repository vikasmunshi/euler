#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 362: Squarefree Factors.

Problem Statement:
    Consider the number 54.
    54 can be factored in 7 distinct ways into one or more factors larger than 1:
    54, 2 x 27, 3 x 18, 6 x 9, 3 x 3 x 6, 2 x 3 x 9 and 2 x 3 x 3 x 3.
    If we require that the factors are all squarefree only two ways remain:
    3 x 3 x 6 and 2 x 3 x 3 x 3.

    Let's call Fsf(n) the number of ways n can be factored into one or more
    squarefree factors larger than 1, so Fsf(54)=2.

    Let S(n) be sum Fsf(k) for k = 2 to n.

    S(100)=193.

    Find S(10000000000).

URL: https://projecteuler.net/problem=362
"""
from typing import Any

euler_problem: int = 362
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '1DZgplRduPfBk/ZQmfbudwQY8mZdPSi0J8QV0Q=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
