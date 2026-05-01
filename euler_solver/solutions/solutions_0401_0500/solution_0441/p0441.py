#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 441: The Inverse Summation of Coprime Couples.

Problem Statement:
    For an integer M, we define R(M) as the sum of 1/(p * q) for all the integer
    pairs p and q which satisfy all of these conditions:
        1 <= p < q <= M
        p + q >= M
        p and q are coprime.

    We also define S(N) as the sum of R(i) for 2 <= i <= N.
    We can verify that S(2) = R(2) = 1/2, S(10) approximately 6.9147, and S(100)
    approximately 58.2962.

    Find S(10^7). Give your answer rounded to four decimal places.

URL: https://projecteuler.net/problem=441
"""
from typing import Any

euler_problem: int = 441
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
