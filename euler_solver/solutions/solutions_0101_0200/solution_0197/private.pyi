#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 197: A Recursively Defined Sequence.

Problem Statement:
    Given is the function f(x) = floor(2^(30.403243784 - x^2)) * 10^-9 (floor is
    the floor-function). The sequence u_n is defined by u_0 = -1 and
    u_{n+1} = f(u_n).

    Find u_n + u_{n+1} for n = 10^12.
    Give your answer with 9 digits after the decimal point.

Solution Approach:
    Interpret values as integer multiples of 10^-9 so the map reduces to integer
    iterations: v -> floor(2^(30.403243784 - (v/1e9)^2)). Detect the eventual
    cycle (use Floyd or record visited states) and then advance to the requested
    index by fast skipping using the cycle length. Expected time is dominated by
    iterations until the cycle entrance; memory is O(K) if recording visited.

Answer: ...
URL: https://projecteuler.net/problem=197
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 197
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}},
    {'category': 'main', 'input': {'n': 1000000000000}},
    {'category': 'extra', 'input': {'n': 1000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_a_recursively_defined_sequence_p0197_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))