#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 38: Pandigital Multiples.

Problem Statement:
    Take the number 192 and multiply it by each of 1, 2, and 3:
        192 × 1 = 192
        192 × 2 = 384
        192 × 3 = 576
    By concatenating each product we get the 1 to 9 pandigital, 192384576.
    We will call 192384576 the concatenated product of 192 and (1,2,3).

    The same can be achieved by starting with 9 and multiplying by 1, 2, 3, 4,
    and 5, giving the pandigital, 918273645, which is the concatenated product
    of 9 and (1,2,3,4,5).

    What is the largest 1 to 9 pandigital 9-digit number that can be formed as
    the concatenated product of an integer with (1,2, ..., n) where n > 1?

Solution Approach:
    Use brute force search with digit checks. For each number, concatenate its
    products with (1, 2, ...) until length 9. Check if concatenation is 1-9 pandigital.
    Keep track of maximum. Early pruning by length and digit counts reduces search.
    Time complexity depends on search bounds but is feasible with efficient pruning.

Answer: 932718654
URL: https://projecteuler.net/problem=38
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 38
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': 932718654},
]


def is_nine_pandigital(n: int) -> bool:
    if n < 100000000 or n > 999999999:
        return False
    digits: list[int] = [0] * 10
    while n:
        d = n % 10
        if d == 0 or digits[d] == 1:
            return False
        digits[d] = 1
        n //= 10
    return sum(digits[1:]) == 9


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_pandigital_multiples_p0038_s0() -> int:
    for n, x in ((2, 9876), (3, 987), (4, 98), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9)):
        while x > 0:
            number: int = int(''.join([str(i * x) for i in range(1, n + 1)]))
            if is_nine_pandigital(number):
                return number
            x -= 1
    raise ValueError('No solution found')


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
