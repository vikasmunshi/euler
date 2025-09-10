#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 757: Stealthy Numbers.

Problem Statement:
    A positive integer N is stealthy, if there exist positive integers a, b, c, d such
    that ab = cd = N and a + b = c + d + 1.
    For example, 36 = 4 × 9 = 6 × 6 is stealthy.

    You are also given that there are 2851 stealthy numbers not exceeding 10^6.

    How many stealthy numbers are there that don't exceed 10^14?

Solution Approach:
    Use number theory and factorization properties.
    Consider pairs of factor pairs (a,b) and (c,d) of N with equal products but sums
    differing by exactly 1. Find an efficient way to generate and count stealthy numbers
    up to the large limit 10^14 using factor pairs and sum relations.
    Use hashing or sorting of sum pairs plus careful enumeration to achieve good performance.

Answer: ...
URL: https://projecteuler.net/problem=757
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 757
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000000}},
    {'category': 'main', 'input': {'max_limit': 100000000000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_stealthy_numbers_p0757_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))