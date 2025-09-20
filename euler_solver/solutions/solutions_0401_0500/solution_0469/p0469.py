#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 469: Empty Chairs.

Problem Statement:
    In a room N chairs are placed around a round table.
    Knights enter the room one by one and choose at random an available empty chair.
    To have enough elbow room the knights always leave at least one empty chair between
    each other.

    When there aren't any suitable chairs left, the fraction C of empty chairs is determined.
    We also define E(N) as the expected value of C.
    We can verify that E(4) = 1/2 and E(6) = 5/9.

    Find E(10^18). Give your answer rounded to fourteen decimal places in the form
    0.abcdefghijklmn.

URL: https://projecteuler.net/problem=469
"""
from typing import Any

euler_problem: int = 469
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'koozcG8bWyt8+T2p'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
