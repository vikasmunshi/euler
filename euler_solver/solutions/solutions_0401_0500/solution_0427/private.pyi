#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 427: n-sequences.

Problem Statement:
    A sequence of integers S = {s_i} is called an n-sequence if it has n elements
    and each element s_i satisfies 1 ≤ s_i ≤ n. Thus there are n^n distinct n-sequences
    in total.
    For example, the sequence S = {1, 5, 5, 10, 7, 7, 7, 2, 3, 7} is a 10-sequence.

    For any sequence S, let L(S) be the length of the longest contiguous subsequence
    of S with the same value.
    For example, for the given sequence S above, L(S) = 3, because of the three
    consecutive 7's.

    Let f(n) = sum of L(S) for all n-sequences S.

    For example, f(3) = 45, f(7) = 1403689 and f(11) = 481496895121.

    Find f(7,500,000) mod 1,000,000,009.

Solution Approach:
    Use combinatorics and dynamic programming to count occurrences of longest runs
    across all n-sequences efficiently.
    Employ modulo arithmetic for large number handling.
    Analyze patterns to derive a computational formula avoiding enumeration.
    Target O(n) or O(n log n) complexity via mathematical formula and fast summation.

Answer: ...
URL: https://projecteuler.net/problem=427
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 427
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}},
    {'category': 'main', 'input': {'n': 7500000}},
    {'category': 'extra', 'input': {'n': 10000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_n_sequences_p0427_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))