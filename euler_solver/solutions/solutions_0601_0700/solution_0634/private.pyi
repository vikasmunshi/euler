#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 634: Numbers of the Form a^2b^3.

Problem Statement:
    Define F(n) to be the number of integers x ≤ n that can be written in the form
    x = a^2 b^3, where a and b are integers not necessarily different and both greater
    than 1.

    For example, 32 = 2^2 × 2^3 and 72 = 3^2 × 2^3 are the only two integers less than 100
    that can be written in this form. Hence, F(100) = 2.

    Further you are given F(2 × 10^4) = 130 and F(3 × 10^6) = 2014.

    Find F(9 × 10^18).

Solution Approach:
    Use number theory focusing on integer factorizations of the form a^2 b^3.
    Efficiently count integers up to n that fit the form by iterating over possible b values
    and counting valid a values using sqrt and cube root bounds.
    Use fast prime sieves or similar to generate candidates for a and b if needed.
    The problem requires careful optimization to handle the large upper bound 9 × 10^18.

Answer: ...
URL: https://projecteuler.net/problem=634
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 634
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}},
    {'category': 'main', 'input': {'max_limit': 9000000000000000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_numbers_of_the_form_a2b3_p0634_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))