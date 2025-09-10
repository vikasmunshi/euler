#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 513: Integral Median.

Problem Statement:
    ABC is an integral sided triangle with sides a <= b <= c.
    m_C is the median connecting C and the midpoint of AB.
    F(n) is the number of such triangles with c <= n for which m_C has integral length as well.
    F(10) = 3 and F(50) = 165.

    Find F(100000).

Solution Approach:
    Use number theory to enumerate integral triangles with sides (a,b,c).
    Express the median m_C using Apollonius' theorem: m_C^2 = (2a^2 + 2b^2 - c^2)/4.
    Require m_C to be integral, so (2a^2 + 2b^2 - c^2) must be a perfect square times 4.
    Employ efficient iteration over bounds, algebraic manipulations, and caching to count valid triples.
    Complexity reduction involves bounding c and leveraging triangle inequalities early.

Answer: ...
URL: https://projecteuler.net/problem=513
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 513
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 100000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_integral_median_p0513_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))