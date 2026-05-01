#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 745: Sum of Squares II.

Problem Statement:
    For a positive integer, n, define g(n) to be the maximum perfect square that
    divides n.

    For example, g(18) = 9, g(19) = 1.

    Also define
        S(N) = sum from n=1 to N of g(n).

    For example, S(10) = 24 and S(100) = 767.

    Find S(10^14). Give your answer modulo 1 000 000 007.

URL: https://projecteuler.net/problem=745
"""
from typing import Any

euler_problem: int = 745
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
