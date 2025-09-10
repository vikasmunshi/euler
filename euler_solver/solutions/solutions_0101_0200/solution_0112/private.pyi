#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 112: Bouncy Numbers.

Problem Statement:
    Working from left-to-right, if no digit is exceeded by the digit to its
    left it is called an increasing number; for example, 134468.

    Similarly, if no digit is exceeded by the digit to its right it is called a
    decreasing number; for example, 66420.

    A positive integer that is neither increasing nor decreasing is called a
    "bouncy" number; for example, 155349.

    There are no bouncy numbers below one-hundred, but just over half of the
    numbers below one-thousand (525) are bouncy. The least number for which the
    proportion of bouncy numbers first reaches 50% is 538.

    By the time we reach 21780 the proportion of bouncy numbers is 90%.

    Find the least number for which the proportion of bouncy numbers is
    exactly 99%.

Solution Approach:
    Count non-bouncy numbers (increasing + decreasing - flat/constant) using
    combinatorics (stars-and-bars / combinations with repetition). Key formulae
    count increasing/decreasing numbers by digit-length. Compute proportion of
    bouncy = 1 - non_bouncy / n and search for the least n reaching target%.
    Use either incremental accumulation by digit or digit-wise combinatorics and
    a simple loop or binary search. Time: roughly O(digits) per check; space O(1).

Answer: ...
URL: https://projecteuler.net/problem=112
"""
from __future__ import annotations

from itertools import count
from typing import Any

from euler_solver.c_libs import use_wrapped_c_function
from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 112
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'target_percentage': 50}},
    {'category': 'dev', 'input': {'target_percentage': 90}},
    {'category': 'main', 'input': {'target_percentage': 99}},
]


@use_wrapped_c_function('p0112')
def euler112(target_percentage: int) -> int: ...

@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_bouncy_numbers_p0112_s0(*, target_percentage: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
