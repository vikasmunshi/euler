#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 40: Champernowne's Constant.

Problem Statement:
    An irrational decimal fraction is created by concatenating the positive integers:
    0.123456789101112131415161718192021...

    It can be seen that the 12th digit of the fractional part is 1.

    If d_n represents the nth digit of the fractional part, find the value of the
    following expression:
    d_1 × d_10 × d_100 × d_1000 × d_10000 × d_100000 × d_1000000

Solution Approach:
    Identify which integer each digit d_n falls into by cumulative counting digit
    lengths for ranges of integers (1-digit, 2-digit, etc.).
    Extract exact digit by indexing into the integer.
    Multiply extracted digits.
    Use math and efficient indexing rather than building the entire fraction.
    Time complexity is O(log n) due to digit range jumps.

Answer: ...
URL: https://projecteuler.net/problem=40
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 40
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'i': 1}},
    {'category': 'preliminary', 'input': {'i': 2}},
    {'category': 'preliminary', 'input': {'i': 3}},
    {'category': 'preliminary', 'input': {'i': 4}},
    {'category': 'preliminary', 'input': {'i': 5}},
    {'category': 'preliminary', 'input': {'i': 6}},
    {'category': 'main', 'input': {'i': 7}},
    {'category': 'extended', 'input': {'i': 8}},
    {'category': 'extended', 'input': {'i': 9}},
    {'category': 'extended', 'input': {'i': 10}},
    {'category': 'extended', 'input': {'i': 11}}
]


def get_nth_digit_champernowne_s_constant(n: int) -> int: ...

@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_champernownes_constant_p0040_s0(*, i: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
