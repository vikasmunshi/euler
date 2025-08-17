#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 80: Square Root Digital Expansion.

Problem Statement:
    It is well known that if the square root of a natural number is not an integer,
    then it is irrational. The decimal expansion of such square roots is infinite
    without any repeating pattern at all.

    The square root of two is 1.41421356237309504880..., and the digital sum of the
    first one hundred decimal digits is 475.

    For the first one hundred natural numbers, find the total of the digital sums of
    the first one hundred decimal digits for all the irrational square roots.

Solution Approach:
    Use high-precision arithmetic or digit-by-digit algorithms to compute the first 100
    decimal digits of square roots for non-square natural numbers. Sum the digits for
    each, then total over all. Efficient big integer arithmetic and digit extraction
    methods based on long division or Newton iteration are key.

Answer: 40886
URL: https://projecteuler.net/problem=80
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.maths.sqrt import sqrt_binary_search, sqrt_heron_method
from euler_solver.maths.sum_digits import sum_digits
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 80
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'digits': 100, 'max_num': 2}},
    {'category': 'main', 'input': {'digits': 100, 'max_num': 99}},
    {'category': 'extended', 'input': {'digits': 100, 'max_num': 999}}
]


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_square_root_digital_expansion_p0080_s0(*, digits: int, max_num: int) -> int:
    result: int = 0
    for i in range(2, max_num + 1):
        if i ** 0.5 % 1 == 0:
            continue
        result += sum_digits(sqrt_heron_method(i, digits))
    return result


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_square_root_digital_expansion_p0080_s1(*, digits: int, max_num: int) -> int:
    result: int = 0
    for i in range(2, max_num + 1):
        if i ** 0.5 % 1 == 0:
            continue
        result += sum_digits(sqrt_binary_search(i, digits))
    return result


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
