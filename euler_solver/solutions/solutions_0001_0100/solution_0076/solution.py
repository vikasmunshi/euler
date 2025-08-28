#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 76: Counting Summations.

Problem Statement:
    It is possible to write five as a sum in exactly six different ways:
    4 + 1
    3 + 2
    3 + 1 + 1
    2 + 2 + 1
    2 + 1 + 1 + 1
    1 + 1 + 1 + 1 + 1

    How many different ways can one hundred be written as a sum of at least
    two positive integers?

Solution Approach:
    Use number theory and combinatorics related to integer partitions.
    Employ dynamic programming to count partitions efficiently.
    Utilize the generating function or recurrence relations for partitions.
    Expected time complexity is O(n²) with n=100 feasible in Python.

Answer: 190569291
URL: https://projecteuler.net/problem=76
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.maths.integer_partitions import (get_partitions_simple_recursion,
                                                   num_partitions_recursive_pentagonal,
                                                   num_partitions_simple_recursion)
from euler_solver.setup import evaluate, register_solution, set_resource_limits

euler_problem: int = 76
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'num': 5}},
    {'category': 'preliminary', 'input': {'num': 50}},
    {'category': 'main', 'input': {'num': 100}},
    {'category': 'extended', 'input': {'num': 1000}}
]


@register_solution(euler_problem=euler_problem, max_test_case=None)
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def solve_counting_summations_p0076_s0(*, num: int) -> int:
    result: int = num_partitions_recursive_pentagonal(number=num) - 1
    return result


@register_solution(euler_problem=euler_problem, max_test_case=3)
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def solve_counting_summations_p0076_s1(*, num: int) -> int:
    return num_partitions_simple_recursion(number=num, slots=num) - 1


@register_solution(euler_problem=euler_problem, max_test_case=2, allow_max_override=False)
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def solve_counting_summations_p0076_s2(*, num: int) -> int:
    return len(get_partitions_simple_recursion(number=num, slots=num)) - 1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
