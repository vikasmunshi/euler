#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 396: Weak Goodstein Sequence.

Problem Statement:
    For any positive integer n, the nth weak Goodstein sequence {g1, g2, g3, ...}
    is defined as:
    g1 = n
    for k > 1, gk is obtained by writing g{k-1} in base k, interpreting it as a
    base k+1 number, and subtracting 1.
    The sequence terminates when gk becomes 0.

    For example, the 6th weak Goodstein sequence is {6, 11, 17, 25, ...}:
    g1 = 6.
    g2 = 11 since 6 = 110_2, 110_3 = 12, and 12 - 1 = 11.
    g3 = 17 since 11 = 102_3, 102_4 = 18, and 18 - 1 = 17.
    g4 = 25 since 17 = 101_4, 101_5 = 26, and 26 - 1 = 25.

    It can be shown that every weak Goodstein sequence terminates.

    Let G(n) be the number of nonzero elements in the nth weak Goodstein
    sequence. It can be verified that G(2) = 3, G(4) = 21 and G(6) = 381.
    It can also be verified that sum G(n) = 2517 for 1 <= n < 8.

    Find the last 9 digits of sum G(n) for 1 <= n < 16.

Solution Approach:
    Simulate weak Goodstein sequences for n from 1 to max_limit-1. Represent
    integers by their digits in base k when computing the step to base k+1.
    Use integer arithmetic: value = sum digits*(k+1)^i - 1. Use memoization
    for repeated (k, value) states to avoid redundant work. Track counts of
    nonzero terms G(n) and sum them, returning last 9 digits as required.
    Time complexity depends on sequence growth but is manageable for max_limit
    up to small tens with efficient base conversion and caching.

Answer: ...
URL: https://projecteuler.net/problem=396
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 396
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 8}},
    {'category': 'main', 'input': {'max_limit': 16}},
    {'category': 'extra', 'input': {'max_limit': 20}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_weak_goodstein_sequence_p0396_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))