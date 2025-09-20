#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 269: Polynomials with at Least One Integer Root.

Problem Statement:
    A root or zero of a polynomial P(x) is a solution to the equation P(x) = 0.
    Define P_n as the polynomial whose coefficients are the digits of n.
    For example, P_5703(x) = 5x^3 + 7x^2 + 3.

    We can see that:
    P_n(0) is the last digit of n.
    P_n(1) is the sum of the digits of n.
    P_n(10) is n itself.

    Define Z(k) as the number of positive integers, n, not exceeding k for which
    the polynomial P_n has at least one integer root.

    It can be verified that Z(100000) is 14696.

    What is Z(10^16)?

URL: https://projecteuler.net/problem=269
"""
from typing import Any

euler_problem: int = 269
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
