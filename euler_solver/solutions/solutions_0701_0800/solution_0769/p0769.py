#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 769: Binary Quadratic Form II.

Problem Statement:
    Consider the following binary quadratic form:
        f(x,y) = x^2 + 5xy + 3y^2

    A positive integer q has a primitive representation if there exist positive integers x and y
    such that q = f(x,y) and gcd(x,y)=1.

    We are interested in primitive representations of perfect squares. For example:
        17^2 = f(1,9)
        87^2 = f(13,40) = f(46,19)

    Define C(N) as the total number of primitive representations of z^2 for 0 < z <= N.
    Multiple representations are counted separately, so for example z=87 is counted twice.

    You are given C(10^3) = 142 and C(10^6) = 142463.

    Find C(10^14).

URL: https://projecteuler.net/problem=769
"""
from typing import Any

euler_problem: int = 769
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
