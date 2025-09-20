#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 630: Crossed Lines.

Problem Statement:
    Given a set, L, of unique lines, let M(L) be the number of lines in the
    set and let S(L) be the sum over every line of the number of times that
    line is crossed by another line in the set. For example, two sets of three
    lines are shown below:

    In both cases M(L) is 3 and S(L) is 6: each of the three lines is crossed
    by two other lines. Note that even if the lines cross at a single point,
    all of the separate crossings of lines are counted.

    Consider points (T_2k-1, T_2k), for integer k ≥ 1, generated in the following way:

    S_0 = 290797
    S_n+1 = S_n^2 mod 50515093
    T_n = (S_n mod 2000) - 1000

    For example, the first three points are: (527, 144), (-488, 732), (-454, -947).
    Given the first n points generated in this manner, let L_n be the set of unique
    lines that can be formed by joining each point with every other point, the lines
    being extended indefinitely in both directions. We can then define M(L_n) and
    S(L_n) as described above.

    For example, M(L_3) = 3 and S(L_3) = 6. Also M(L_100) = 4948 and S(L_100) = 24477690.

    Find S(L_2500).

URL: https://projecteuler.net/problem=630
"""
from typing import Any

euler_problem: int = 630
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 2500}, 'answer': None},
    {'category': 'extra', 'input': {'n': 5000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
