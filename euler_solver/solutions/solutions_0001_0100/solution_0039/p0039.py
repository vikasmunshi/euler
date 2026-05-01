#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 39: Integer Right Triangles.

Problem Statement:
    If p is the perimeter of a right angle triangle with integral length sides,
    {a, b, c}, there are exactly three solutions for p = 120.

    {20,48,52}, {24,45,51}, {30,40,50}

    For which value of p ≤ 1000, is the number of solutions maximised?

Solution Approach:
    Enumerate all integer triples (a, b, c) with a+b+c = p and a^2 + b^2 = c^2.
    Use number theory properties to reduce search space. Efficiently check all p ≤ 1000.
    Use a counting array to record number of solutions for each perimeter.
    Time complexity roughly O(p^2).

Answer: 840
URL: https://projecteuler.net/problem=39
"""
from __future__ import annotations

from collections import Counter
from math import gcd
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 39
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_perimeter': 100}, 'answer': 60},
    {'category': 'main', 'input': {'max_perimeter': 1000}, 'answer': 840},
    {'category': 'extra', 'input': {'max_perimeter': 10000}, 'answer': 5040},
    {'category': 'extra', 'input': {'max_perimeter': 100000}, 'answer': 55440},
    {'category': 'extra', 'input': {'max_perimeter': 1000000}, 'answer': 720720},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_integer_right_triangles_p0039_s0(*, max_perimeter: int) -> int:
    triangle_perimeters = []
    for n in range(1, (int(8 * max_perimeter ** 0.5) - 6) // 8, 1):
        for m in (m for m in range(n + 1, (int((4 + 8 * max_perimeter) ** 0.5) - 2 * n) // 4, 2) if gcd(m, n) == 1):
            triangle_perimeters.append((perimeter := (2 * m * (m + n))))
            for k in range(2, max_perimeter // perimeter):
                triangle_perimeters.append(k * perimeter)
    return Counter(triangle_perimeters).most_common()[0][0]


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
