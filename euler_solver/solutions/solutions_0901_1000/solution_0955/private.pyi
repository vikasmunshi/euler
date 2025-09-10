#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 955: Finding Triangles.

Problem Statement:
    A sequence (a_n)_{n >= 0} starts with a_0 = 3 and for each n >= 0,
    if a_n is a triangle number, then a_{n + 1} = a_n + 1;
    otherwise, a_{n + 1} = 2a_n - a_{n - 1} + 1.

    A triangle number is a number of the form m(m + 1)/2 for some integer m.

    The sequence begins:
    3, 4, 6, 7, 9, 12, 16, 21, 22, 24, 27, 31, 36, 37, 39, 42, ...
    where triangle numbers are marked in the sequence.

    The 10th triangle number in the sequence is a_{2964} = 1439056.
    Find the index n such that a_n is the 70th triangle number in the sequence.

Solution Approach:
    Use dynamic programming to generate terms of the sequence efficiently.
    Identify triangle numbers by checking if 8x+1 is a perfect square.
    Optimize by storing previously computed terms.
    Locate the index of the k-th triangle number in the sequence.
    This approach involves number theory (triangle numbers) and DP.

Answer: ...
URL: https://projecteuler.net/problem=955
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 955
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 10}},
    {'category': 'main', 'input': {'k': 70}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_finding_triangles_p0955_s0(*, k: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))