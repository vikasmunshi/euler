#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 170: Pandigital Concatenating Products.

Problem Statement:
    Take the number 6 and multiply it by each of 1273 and 9854:
    6 x 1273 = 7638
    6 x 9854 = 59124

    By concatenating these products we get the 1 to 9 pandigital 763859124.
    We will call 763859124 the "concatenated product of 6 and (1273,9854)".
    Notice too, that the concatenation of the input numbers, 612739854, is also
    1 to 9 pandigital.

    The same can be done for 0 to 9 pandigital numbers.

    What is the largest 0 to 9 pandigital 10-digit concatenated product of an
    integer with two or more other integers, such that the concatenation of the
    input numbers is also a 0 to 9 pandigital 10-digit number?

Solution Approach:
    Search space is over 0-9 pandigital 10-digit concatenations of the input numbers.
    For each pandigital arrangement, split the digits into a base integer and two
    or more following integers. Compute the products of the base with each part
    and check if concatenating those products yields a 0-9 pandigital 10-digit
    number. Use fast digit-counting and early pruning to reject impossible splits.
    Complexity dominated by permutations and split positions but heavy pruning
    (length checks, leading-zero rules) makes exhaustive search feasible in Python.

Answer: ...
URL: https://projecteuler.net/problem=170
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 170
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_pandigital_concatenating_products_p0170_s0() -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))