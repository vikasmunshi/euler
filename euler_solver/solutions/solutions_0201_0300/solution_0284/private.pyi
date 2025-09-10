#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 284: Steady Squares.

Problem Statement:
    The 3-digit number 376 in the decimal numbering system is an example of numbers
    with the special property that its square ends with the same digits: 376^2 =
    141376. Let's call a number with this property a steady square.

    Steady squares can also be observed in other numbering systems. In the base
    14 numbering system, the 3-digit number c37 is also a steady square: c37^2 =
    aa0c37, and the sum of its digits is c+3+7=18 in the same numbering system.
    The letters a, b, c and d are used for the 10, 11, 12 and 13 digits
    respectively, in a manner similar to the hexadecimal numbering system.

    For 1 ≤ n ≤ 9, the sum of the digits of all the n-digit steady squares in the
    base 14 numbering system is 2d8 (582 decimal). Steady squares with leading
    0's are not allowed.

    Find the sum of the digits of all the n-digit steady squares in the base 14
    numbering system for 1 ≤ n ≤ 10000 (decimal) and give your answer in the base
    14 system using lower case letters where necessary.

Solution Approach:
    Reduce the steady-square condition to x^2 ≡ x (mod 14^n). Use the prime
    factorization 14^n = 2^n * 7^n and solve the congruence modulo each prime
    power, lifting solutions as needed (Hensel lifting). Combine solutions by
    the Chinese Remainder Theorem to enumerate residues modulo 14^n.
    Count only representatives with no leading base-14 zeroes and compute their
    base-14 digit sums efficiently by exploiting the residue structure and any
    periodic or recurrence behavior. Expected complexity is polylog per n with
    overall O(max_n) or better with optimizations.

Answer: ...
URL: https://projecteuler.net/problem=284
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 284
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 9}},
    {'category': 'main', 'input': {'max_n': 10000}},
    {'category': 'extra', 'input': {'max_n': 20000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_steady_squares_p0284_s0(*, max_n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))