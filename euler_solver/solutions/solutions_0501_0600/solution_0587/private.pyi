#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 587: Concave Triangle.

Problem Statement:
    A square is drawn around a circle as shown in the diagram below on the left.
    We shall call the blue shaded region the L-section.
    A line is drawn from the bottom left of the square to the top right as shown
    in the diagram on the right.
    We shall call the orange shaded region a concave triangle.

    It should be clear that the concave triangle occupies exactly half of the L-section.

    Two circles are placed next to each other horizontally, a rectangle is drawn
    around both circles, and a line is drawn from the bottom left to the top right
    as shown in the diagram below.

    This time the concave triangle occupies approximately 36.46% of the L-section.

    If n circles are placed next to each other horizontally, a rectangle is drawn
    around the n circles, and a line is drawn from the bottom left to the top right,
    then it can be shown that the least value of n for which the concave triangle
    occupies less than 10% of the L-section is n = 15.

    What is the least value of n for which the concave triangle occupies less
    than 0.1% of the L-section?

Solution Approach:
    Use geometry and algebraic analysis of areas formed by circles and line segments.
    Employ iterative or exact formulas for the concave triangle and L-section areas.
    Use numeric methods or closed-form expressions to find the threshold n.
    Time complexity depends on method; likely O(n) or better with analytic formula.

Answer: ...
URL: https://projecteuler.net/problem=587
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 587
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 2}},
    {'category': 'main', 'input': {'max_n': 15}},
    {'category': 'extra', 'input': {'max_n': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_concave_triangle_p0587_s0(*, max_n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))