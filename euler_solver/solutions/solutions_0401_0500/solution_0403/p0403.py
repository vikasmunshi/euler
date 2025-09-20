#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 403: Lattice Points Enclosed by Parabola and Line.

Problem Statement:
    For integers a and b, we define D(a, b) as the domain enclosed by the parabola
    y = x^2 and the line y = a*x + b:
        D(a, b) = {(x, y) | x^2 <= y <= a*x + b}.

    L(a, b) is defined as the number of lattice points contained in D(a, b).

    For example, L(1, 2) = 8 and L(2, -1) = 1.

    We also define S(N) as the sum of L(a, b) for all the pairs (a, b) such that the
    area of D(a, b) is a rational number and |a|, |b| <= N.

    We can verify that S(5) = 344 and S(100) = 26709528.

    Find S(10^12). Give your answer mod 10^8.

URL: https://projecteuler.net/problem=403
"""
from typing import Any

euler_problem: int = 403
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 5}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '9N5mC1wyw8uaNVuF2xQPmQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
