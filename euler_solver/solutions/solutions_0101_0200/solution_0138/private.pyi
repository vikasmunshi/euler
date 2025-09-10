#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 138: Special Isosceles Triangles.

Problem Statement:
    Consider the isosceles triangle with base length b = 16 and legs L = 17.
    By using the Pythagorean theorem it can be seen that the height
    h = sqrt(17^2 - 8^2) = 15, which is one less than the base length.

    With b = 272 and L = 305, we get h = 273, which is one more than the
    base length, and this is the second smallest isosceles triangle with the
    property that h = b ± 1.

    Find sum L for the twelve smallest isosceles triangles for which
    h = b ± 1 and b, L are positive integers.

Solution Approach:
    Reduce the geometry to a Diophantine equation (a Pell-type equation)
    by letting a = b/2 and using L^2 = h^2 + a^2 with h = b ± 1. This yields
    a quadratic Pell recurrence for integer solutions. Generate solutions
    via the fundamental solution and recurrence relations, collect the
    smallest n legs L, and sum them. Time: O(n) operations with arithmetic
    on integers whose size grows linearly with n. Space: O(1) extra.

Answer: ...
URL: https://projecteuler.net/problem=138
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 138
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}},
    {'category': 'main', 'input': {'n': 12}},
    {'category': 'extra', 'input': {'n': 20}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_special_isosceles_triangles_p0138_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))