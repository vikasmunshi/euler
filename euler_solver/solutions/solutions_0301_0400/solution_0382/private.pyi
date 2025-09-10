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

Solution Approach:
    Key observation: a set S of distinct positive lengths generates a polygon
    iff |S| >= 3 and 2*max(S) < sum(S) (polygon inequality). Count subsets of
    U_n satisfying this inequality.

    Use combinatorics and the linear recurrence of s_n to exploit structure:
    precompute relations among prefix sums and counts for a block of terms,
    then use matrix exponentiation / linear recurrences to extend to n up to
    10^18. Work modulo 10^9 to obtain last 9 digits. Complexity: poly(k)*log n.

Answer: ...
URL: https://projecteuler.net/problem=382
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 382
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}},
    {'category': 'main', 'input': {'n': 1000000000000000000}},
    {'category': 'extra', 'input': {'n': 25}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_generating_polygons_p0382_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))