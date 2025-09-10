#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 258: A Lagged Fibonacci Sequence.

Problem Statement:
    A sequence is defined as:
    g_k = 1, for 0 <= k <= 1999
    g_k = g_{k-2000} + g_{k-1999}, for k >= 2000.
    Find g_k mod 20092010 for k = 10^18.

Solution Approach:
    Treat this as a linear recurrence of order 2000. Use matrix exponentiation
    of the companion matrix or a fast linear-recurrence exponentiation to step
    the state to index k using binary exponentiation. Exploit the companion
    matrix sparsity to multiply in O(n^2) or better per squaring. Expected
    complexity roughly O(n^2 log k) time and O(n) space, working modulo m.

Answer: ...
URL: https://projecteuler.net/problem=258
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 258
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 10, 'modulus': 1000}},
    {'category': 'main', 'input': {'k': 1000000000000000000, 'modulus': 20092010}},
    {'category': 'extra', 'input': {'k': 1000000000000, 'modulus': 20092010}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_a_lagged_fibonacci_sequence_p0258_s0(*, k: int, modulus: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))