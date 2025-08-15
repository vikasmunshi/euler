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

Answer: TBD
URL: https://projecteuler.net/problem=39
"""
from __future__ import annotations

from typing import Any

from euler.logger import logger
from euler.setup import evaluate, register_solution

euler_problem: int = 39
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'max_perimeter': 100}},
    {'category': 'main', 'input': {'max_perimeter': 1000}},
    {'category': 'extended', 'input': {'max_perimeter': 10000}},
    {'category': 'extended', 'input': {'max_perimeter': 100000}},
    {'category': 'extended', 'input': {'max_perimeter': 1000000}}
]


@register_solution(euler_problem=euler_problem, test_cases=test_cases[:])
def solve_integer_right_triangles_p0039_s0(*, max_perimeter: int) -> int:
    ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
