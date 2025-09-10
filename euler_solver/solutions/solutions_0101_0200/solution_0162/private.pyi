#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 162: Hexadecimal Numbers.

Problem Statement:
    In the hexadecimal number system numbers are represented using 16 different
    digits: 0,1,2,3,4,5,6,7,8,9,A,B,C,D,E,F.

    The hexadecimal number AF when written in the decimal number system equals
    10 * 16 + 15 = 175.

    In the 3-digit hexadecimal numbers 10A, 1A0, A10, and A01 the digits 0, 1
    and A are all present. Like numbers written in base ten we write
    hexadecimal numbers without leading zeroes.

    How many hexadecimal numbers containing at most sixteen hexadecimal digits
    exist with all of the digits 0, 1, and A present at least once?
    Give your answer as a hexadecimal number.

    (A, B, C, D, E and F in upper case, without any leading or trailing code
    that marks the number as hexadecimal and without leading zeroes, e.g. 1A3F
    and not: 1a3f and not 0x1a3f and not 1A3F and not #1A3F and not
    0000001A3F)

Solution Approach:
    Use combinatorics and inclusion–exclusion over lengths L = 1..max_digits.
    For each L count valid strings of length L with no leading zero, over the
    16 hex symbols. Use inclusion–exclusion to exclude strings missing 0, 1 or
    A (treating cases where zero is excluded carefully because of the leading
    digit restriction). Sum counts for all L. Complexity O(max_digits) time and
    O(1) extra space; arithmetic on big integers as needed.

Answer: ...
URL: https://projecteuler.net/problem=162
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 162
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_digits': 3}},
    {'category': 'main', 'input': {'max_digits': 16}},
    {'category': 'extra', 'input': {'max_digits': 20}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_hexadecimal_numbers_p0162_s0(*, max_digits: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))