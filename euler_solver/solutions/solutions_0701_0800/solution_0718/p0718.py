#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 718: Unreachable Numbers.

Problem Statement:
    Consider the equation
    17^p a + 19^p b + 23^p c = n where a, b, c and p are positive integers,
    i.e. a,b,c,p > 0.

    For a given p there are some values of n > 0 for which the equation cannot
    be solved. We call these unreachable values.

    Define G(p) to be the sum of all unreachable values of n for the given value
    of p. For example G(1) = 8253 and G(2)= 60258000.

    Find G(6). Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=718
"""
from typing import Any

euler_problem: int = 718
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'p': 6}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
