#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 193: Squarefree Numbers.

Problem Statement:
    A positive integer n is called squarefree, if no square of a prime divides n,
    thus 1, 2, 3, 5, 6, 7, 10, 11 are squarefree, but not 4, 8, 9, 12.

    How many squarefree numbers are there below 2^50?

URL: https://projecteuler.net/problem=193
"""
from typing import Any

euler_problem: int = 193
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1125899906842624}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1099511627776}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
