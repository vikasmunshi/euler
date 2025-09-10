#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 113: Non-bouncy Numbers.

Problem Statement:
    Working from left-to-right if no digit is exceeded by the digit to its left
    it is called an increasing number; for example, 134468.
    Similarly if no digit is exceeded by the digit to its right it is called a
    decreasing number; for example, 66420.
    We shall call a positive integer that is neither increasing nor decreasing a
    "bouncy" number; for example, 155349.
    As n increases, the proportion of bouncy numbers below n increases such that
    there are only 12951 numbers below one-million that are not bouncy and only
    277032 non-bouncy numbers below 10^10.
    How many numbers below a googol (10^100) are not bouncy?

Solution Approach:
    Use combinatorics to count non-decreasing (increasing) and non-increasing
    (decreasing) digit sequences for each length up to 100. Model these as
    combinations with repetition (stars-and-bars). Subtract numbers counted
    twice (constant-digit numbers) and adjust for leading-zero conventions.
    This yields a closed-form count computed in O(d) time for d=100 and O(1)
    additional space.

Answer: ...
URL: https://projecteuler.net/problem=113
"""
from __future__ import annotations

from math import comb
from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 113
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_max_digits': 6}},
    {'category': 'dev', 'input': {'num_max_digits': 10}},
    {'category': 'main', 'input': {'num_max_digits': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_non_bouncy_numbers_p0113_s0(*, num_max_digits: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
