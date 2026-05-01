#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 759: A Squared Recurrence Relation.

Problem Statement:
    The function f is defined for all positive integers as follows:

        f(1) = 1
        f(2n) = 2 f(n)
        f(2n+1) = 2n + 1 + 2 f(n) + (1/n) f(n)

    It can be proven that f(n) is integer for all values of n.

    The function S(n) is defined as S(n) = sum of f(i)^2 for i from 1 to n.

    For example, S(10) = 1530 and S(10^2) = 4798445.

    Find S(10^16). Give your answer modulo 1 000 000 007.

URL: https://projecteuler.net/problem=759
"""
from typing import Any

euler_problem: int = 759
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'iz0Y+vvSymgIDB9TrRiags7vPaY='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
