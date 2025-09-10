#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 697: Randomly Decaying Sequence.

Problem Statement:
    Given a fixed real number c, define a random sequence (X_n)_{n≥0} by the following
    random process:
        - X_0 = c (with probability 1).
        - For n > 0, X_n = U_n X_{n-1} where U_n is a real number chosen at random
          between zero and one, uniformly, and independently of all previous choices
          (U_m)_{m<n}.

    If we desire there to be precisely a 25% probability that X_100 < 1, then this can
    be arranged by fixing c such that log_10 c ≈ 46.27.

    Suppose now that c is set to a different value, so that there is precisely a 25%
    probability that X_10,000,000 < 1.

    Find log_10 c and give your answer rounded to two places after the decimal point.

Solution Approach:
    Use probability theory and analysis of the product of independent uniform random
    variables. Employ log transformations and the central limit theorem to estimate
    the distribution of log X_n. Use the quantile of the normal distribution to solve
    for log_10 c. This involves statistics and numerical methods, expected O(1) complexity.

Answer: ...
URL: https://projecteuler.net/problem=697
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 697
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 100}},
    {'category': 'main', 'input': {'n': 10000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_randomly_decaying_sequence_p0697_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))