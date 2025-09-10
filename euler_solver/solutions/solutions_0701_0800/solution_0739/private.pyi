#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 739: Summation of Summations.

Problem Statement:
    Take a sequence of length n. Discard the first term then make a sequence of the
    partial summations. Continue to do this over and over until we are left with a
    single term. We define this to be f(n).

    Consider the example where we start with a sequence of length 8:

        1  1  1  1  1  1  1  1
           1  2  3  4  5  6  7
              2  5  9 14 20 27
                 5 14 28 48 75
                   14 42 90 165
                      42 132 297
                         132 429
                            429

    Then the final number is 429, so f(8) = 429.

    For this problem we start with the sequence 1,3,4,7,11,18,29,47,...
    This is the Lucas sequence where two terms are added to get the next term.
    Applying the same process as above we get f(8) = 2663.
    You are also given f(20) = 742296999 modulo 1000000007.

    Find f(10^8). Give your answer modulo 1000000007.

Solution Approach:
    Model the iterative summation process mathematically and use properties of the Lucas
    sequence. Employ efficient combinatorial identities or generating functions to avoid
    explicit repeated summations. Use modular arithmetic for large numbers. Expected to
    use number theory and fast arithmetic techniques for sequences. Aim for O(log n) or
    O(polylog n) solution complexity due to very large input.

Answer: ...
URL: https://projecteuler.net/problem=739
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 739
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 8}},
    {'category': 'main', 'input': {'n': 100000000}},
    {'category': 'extra', 'input': {'n': 200000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_summation_of_summations_p0739_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))