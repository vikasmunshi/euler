#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 802: Iterated Composition.

Problem Statement:
    Let R^2 be the set of pairs of real numbers (x, y). Let π = 3.14159...

    Consider the function f from R^2 to R^2 defined by
    f(x, y) = (x^2 - x - y^2, 2xy - y + π), and its n-th iterated
    composition f^(n)(x, y) = f(f(... f(x, y)...)). For example
    f^(3)(x, y) = f(f(f(x, y))). A pair (x, y) is said to have period n
    if n is the smallest positive integer such that f^(n)(x, y) = (x, y).

    Let P(n) denote the sum of x-coordinates of all points having period not
    exceeding n. Interestingly, P(n) is always an integer. For example,
    P(1) = 2, P(2) = 2, P(3) = 4.

    Find P(10^7) and give your answer modulo 1020340567.

URL: https://projecteuler.net/problem=802
"""
from typing import Any

euler_problem: int = 802
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '+AIuyscFrC2UqZMTlpDrGs0DKBzYyygc'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
