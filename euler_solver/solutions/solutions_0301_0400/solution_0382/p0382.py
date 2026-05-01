#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 382: Generating Polygons.

Problem Statement:
    A polygon is a flat shape consisting of straight line segments that are
    joined to form a closed chain or circuit. A polygon has at least three
    sides and does not self-intersect.

    A set S of positive numbers is said to generate a polygon P if:
        no two sides of P are the same length,
        the length of every side of P is in S, and
        S contains no other value.

    For example:
        The set {3, 4, 5} generates a polygon with sides 3, 4, and 5.
        The set {6, 9, 11, 24} generates a polygon with sides 6, 9, 11, 24.
        The sets {1, 2, 3} and {2, 3, 4, 9} do not generate any polygon.

    Consider the sequence s defined as follows:
        s1 = 1, s2 = 2, s3 = 3
        s_n = s_{n-1} + s_{n-3} for n > 3.

    Let U_n be the set {s1, s2, ..., s_n}. For example,
    U_10 = {1, 2, 3, 4, 6, 9, 13, 19, 28, 41}.
    Let f(n) be the number of subsets of U_n which generate at least one
    polygon. For example, f(5) = 7, f(10) = 501 and f(25) = 18635853.

    Find the last 9 digits of f(10^18).

URL: https://projecteuler.net/problem=382
"""
from typing import Any

euler_problem: int = 382
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 25}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
