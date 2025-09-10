#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 104: Pandigital Fibonacci Ends.

Problem Statement:
    The Fibonacci sequence is defined by the recurrence relation:
        F_n = F_{n - 1} + F_{n - 2}, where F_1 = 1 and F_2 = 1.
    It turns out that F_541, which contains 113 digits, is the first Fibonacci number
    for which the last nine digits are 1-9 pandigital (contain all the digits 1 to 9,
    but not necessarily in order). And F_2749, which contains 575 digits, is the first
    Fibonacci number for which the first nine digits are 1-9 pandigital.
    Given that F_k is the first Fibonacci number for which the first nine digits AND the
    last nine digits are 1-9 pandigital, find k.

Solution Approach:
    Use fast Fibonacci calculation methods to handle large indices efficiently.
    Track only the first 9 digits and last 9 digits of Fibonacci numbers to check
    pandigital conditions. Utilize numeric manipulations and string checks.
    Employ number theory and digit properties for optimization.
    Expected time complexity depends on chosen Fibonacci calculation approach,
    with efficient methods handling the problem within practical constraints.

Answer: ...
URL: https://projecteuler.net/problem=104
"""
from __future__ import annotations

from math import floor, log10, sqrt
from typing import Any, Generator

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution, show_solution
from euler_solver.utils.color_codes import Color as C

euler_problem: int = 104
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]

sqrt_5: float = sqrt(5)
phi: float = (1 + sqrt_5) / 2
log10_sqrt_5: float = log10(sqrt_5)
log10_phi: float = log10(phi)


def is_nine_pandigital(n: int) -> bool: ...

def gen_fibonacci(max_num: int | float = float('inf')) -> Generator[int, None, None]: ...

def gen_fibonacci_modulo_n(n: int) -> Generator[int, None, None]: ...

def k_th_fibonacci_number(k: int) -> int: ...

def most_significant_n_digits_of_k_th_fibonacci_number(k: int, n: int) -> int: ...

def number_of_digits_in_k_th_fibonacci_number(k: int) -> int: ...

def pandigital_fibonacci_ends_show() -> int: ...

@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_pandigital_fibonacci_ends_p0104_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
