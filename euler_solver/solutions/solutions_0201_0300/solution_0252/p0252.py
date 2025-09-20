#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 252: Convex Holes.

Problem Statement:
    Given a set of points on a plane, we define a convex hole to be a convex
    polygon having as vertices any of the given points and not containing any
    of the given points in its interior (points may lie on the perimeter).

    For example, the image in the problem statement shows twenty points and a
    few convex holes. The red heptagon shown has area 1049694.5, which is the
    maximum area convex hole for that example set.

    For the example we used the first 20 points (T_{2k-1}, T_{2k}), for
    k = 1,2,...,20, produced with the pseudo-random generator:
        S_0 = 290797
        S_{n+1} = S_n^2 mod 50515093
        T_n = (S_n mod 2000) - 1000
    i.e. (527, 144), (-488, 732), (-454, -947), ...

    What is the maximum area for a convex hole on the set containing the
    first 500 points in the pseudo-random sequence? Specify your answer
    including one digit after the decimal point.

URL: https://projecteuler.net/problem=252
"""
from typing import Any

euler_problem: int = 252
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 20}, 'answer': None},
    {'category': 'main', 'input': {'n': 500}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
