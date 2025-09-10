#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 330: Euler's Number.

Problem Statement:
    An infinite sequence of real numbers a(n) is defined for all integers n as
    follows:
    a(n) = 1 for n < 0
    a(n) = sum_{i=1}^infty a(n - i)/i! for n >= 0

    For example,
    a(0) = 1/1! + 1/2! + 1/3! + ... = e - 1
    a(1) = (e - 1)/1! + 1/2! + 1/3! + ... = 2e - 3
    a(2) = (2e - 3)/1! + (e - 1)/2! + 1/3! + ... = (7/2)e - 6

    with e = 2.7182818... being Euler's constant.

    It can be shown that a(n) is of the form (A(n)e + B(n))/n! for integers
    A(n) and B(n).

    For example, a(10) = (328161643e - 652694486)/10!.

    Find A(10^9) + B(10^9) and give your answer mod 77777777.

Solution Approach:
    Model the sequence via exponential generating functions to obtain recurrences
    for the integer sequences A(n) and B(n). Reduce the problem to a linear
    recurrence or a small-dimensional linear transformation modulo M = 77777777.
    Compute A(n) and B(n) (or directly A(n)+B(n) mod M) using fast exponentiation
    of the recurrence (matrix exponentiation) in O(k^3 log n) time for small k
    and O(k^2) space, where k is the recurrence order.

Answer: ...
URL: https://projecteuler.net/problem=330
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 330
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}},
    {'category': 'main', 'input': {'n': 1000000000}},
    {'category': 'extra', 'input': {'n': 1000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_eulers_number_p0330_s0(*, n: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))