#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 30: Digit Fifth Powers.

Problem Statement:
    Surprisingly there are only three numbers that can be written as the sum of
    fourth powers of their digits:
        1634 = 1^4 + 6^4 + 3^4 + 4^4
        8208 = 8^4 + 2^4 + 0^4 + 8^4
        9474 = 9^4 + 4^4 + 7^4 + 4^4

    As 1 = 1^4 is not a sum it is not included.

    The sum of these numbers is 1634 + 8208 + 9474 = 19316.

    Find the sum of all the numbers that can be written as the sum of fifth powers
    of their digits.

Solution Approach:
    Enumerate numbers up to a reasoned upper bound based on digit count and 9^5 max
    contribution. For each number, sum the fifth powers of its digits and check equality.
    Use precomputed digit fifth powers for efficiency.
    Expected complexity depends on the upper bound but feasible with simple iteration.

Answer: 443839
URL: https://projecteuler.net/problem=30
"""
from __future__ import annotations

from itertools import combinations_with_replacement
from math import ceil, log
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 30
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': 19316},
    {'category': 'main', 'input': {'n': 5}, 'answer': 443839},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_digit_fifth_powers_p0030_s0(*, n: int) -> int:
    upper_bound_num_digits = ceil(log(n * 9 ** n, 10))
    return sum((num for digits in combinations_with_replacement(range(10), upper_bound_num_digits) if
                (num := sum((x ** n for x in digits))) > 9 and num == sum((int(x) ** n for x in str(num)))))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
