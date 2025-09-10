#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 75: Singular Integer Right Triangles.

Problem Statement:
    It turns out that 12 cm is the smallest length of wire that can be bent to
    form an integer sided right angle triangle in exactly one way, but there are
    many more examples.

    12 cm: (3,4,5)
    24 cm: (6,8,10)
    30 cm: (5,12,13)
    36 cm: (9,12,15)
    40 cm: (8,15,17)
    48 cm: (12,16,20)

    In contrast, some lengths of wire, like 20 cm, cannot be bent to form an
    integer sided right angle triangle, and other lengths allow more than one
    solution to be found; for example, using 120 cm it is possible to form
    exactly three different integer sided right angle triangles.

    120 cm: (30,40,50), (20,48,52), (24,45,51)

    Given that L is the length of the wire, for how many values of L ≤ 1 500 000
    can exactly one integer sided right angle triangle be formed?

Solution Approach:
    Use number theory and Euclid's formula to generate all primitive Pythagorean
    triples. Scale them to find all integer right triangles up to max length L.
    Count wire lengths having exactly one associated triangle using efficient
    aggregation. Time complexity roughly O(L log log L) using a sieve-like approach.

Answer: ...
URL: https://projecteuler.net/problem=75
"""
from __future__ import annotations

from math import gcd
from typing import Any, Dict, Generator

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 75
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_perimeter': 50}},
    {'category': 'main', 'input': {'max_perimeter': 1500000}},
    {'category': 'extra', 'input': {'max_perimeter': 10000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_singular_integer_right_triangles_p0075_s0(*, max_perimeter: int) -> int: ...

def gen_pythagorean_triangle_perimeters(*, max_perimeter: int) -> Generator[int, None, None]: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
