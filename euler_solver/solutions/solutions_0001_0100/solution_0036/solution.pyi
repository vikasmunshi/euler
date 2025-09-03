#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 36: Double-base Palindromes.

Problem Statement:
    The decimal number, 585 = 1001001001_2 (binary), is palindromic in both bases.

    Find the sum of all numbers, less than one million, which are palindromic in
    base 10 and base 2.

    (Please note that the palindromic number, in either base, may not include leading
    zeros.)

Solution Approach:
    Check each number less than one million for palindrome property in decimal and
    binary. Efficient palindrome checks can be done by string reversal. Sum all
    qualifying numbers. Time complexity primarily O(N log N) for conversion and checks.

Answer: ...
URL: https://projecteuler.net/problem=36
"""
from __future__ import annotations

from typing import Any, Generator

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 36
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'max_digits': 1}},
    {'category': 'preliminary', 'input': {'max_digits': 2}},
    {'category': 'preliminary', 'input': {'max_digits': 3}},
    {'category': 'preliminary', 'input': {'max_digits': 4}},
    {'category': 'main', 'input': {'max_digits': 6}},
    {'category': 'extended', 'input': {'max_digits': 9}}
]


def generate_decimal_palindromes(max_digits: int) -> Generator[int, None, None]: ...

@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_double_base_palindromes_p0036_s0(*, max_digits: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
