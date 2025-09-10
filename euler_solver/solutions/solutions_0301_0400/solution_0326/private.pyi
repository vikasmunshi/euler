#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 326: Modulo Summations.

Problem Statement:
    Let a_n be a sequence recursively defined by: a_1 = 1, and
    a_n = (sum_{k=1}^{n-1} k * a_k) mod n.

    So the first 10 elements of a_n are: 1, 1, 0, 3, 0, 3, 5, 4, 1, 9.

    Let f(N, M) represent the number of pairs (p, q) such that:
    1 <= p <= q <= N and (sum_{i=p}^q a_i) mod M = 0.

    It can be seen that f(10,10) = 4 with the pairs (3,3), (5,5), (7,9)
    and (9,10).

    You are also given that f(10^4,10^3) = 97158.

    Find f(10^12,10^6).

Solution Approach:
    Analyze the recurrence to express a_n in terms of a weighted prefix sum
    S_{n-1} = sum_{k=1}^{n-1} k * a_k, so a_n = S_{n-1} mod n. Use number
    theory to understand residues of a_n modulo M and any periodicity
    properties that arise when reducing indices modulo factors of M.

    Reduce the counting problem to prefix sums modulo M and count equal
    residues: f(N,M) equals sum over residues r of C(c_r,2)+c_r where c_r is
    frequency of prefix-sum residue r. Compute frequencies without iterating
    to N by grouping indices with the same contribution using arithmetic
    progressions, multiplicative structure, and fast combinatorics.

    Aim for an algorithm sublinear in N (heuristic target O(M log N) or
    similar) that relies on modular arithmetic, divisor grouping and counting.

Answer: ...
URL: https://projecteuler.net/problem=326
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 326
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 10, 'M': 10}},
    {'category': 'main', 'input': {'N': 1000000000000, 'M': 1000000}},
    {'category': 'extra', 'input': {'N': 1000000, 'M': 1000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_modulo_summations_p0326_s0(*, N: int, M: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))