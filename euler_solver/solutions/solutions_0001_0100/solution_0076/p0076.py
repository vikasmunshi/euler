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

from functools import lru_cache
from itertools import count
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution, set_resource_limits

euler_problem: int = 76
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num': 5}, 'answer': 6},
    {'category': 'dev', 'input': {'num': 50}, 'answer': 204225},
    {'category': 'main', 'input': {'num': 100}, 'answer': 190569291},
    {'category': 'extra', 'input': {'num': 1000}, 'answer': 24061467864032622473692149727990},
]


@lru_cache(maxsize=None)
def pentagonal(x: int) -> int:
    return x * (3 * x - 1) // 2  # pentagonal number formula


@lru_cache(maxsize=None)
def num_partitions_recursive_pentagonal(number: int) -> int:
    if number <= 0:
        result = int(number == 0)
        return result
    result = 0
    for n in count(1):
        p_1 = num_partitions_recursive_pentagonal(number - pentagonal(n))
        p_2 = num_partitions_recursive_pentagonal(number - pentagonal(-n))
        result += ((-1, +1)[n % 2]) * (p_1 + p_2)
        if p_1 == 0 and p_2 == 0:
            break
    return result


@lru_cache(maxsize=None)
def num_partitions_simple_recursion(*, number: int, slots: int) -> int:
    if number < 0 or slots < 0:
        raise ValueError('number and slots must be non-negative')
    if number < slots:
        raise ValueError('number must be greater than or equal to slots')
    if number <= 1:
        return number
    return sum(num_partitions_simple_recursion(number=number - n, slots=min(number - n, n))
               for n in range(1, slots + 1)) + (1 if number <= slots else 0)


@lru_cache(maxsize=None)
def get_partitions_simple_recursion(*, number: int, slots: int, safe_limit: int | None = 50) -> list[list[int]]:
    if safe_limit and number > safe_limit:
        raise OverflowError(f'number must be less than {safe_limit=}')
    if number < 0 or slots < 0:
        raise ValueError('number and slots must be non-negative')
    if number < slots:
        raise ValueError('number must be greater than or equal to slots')
    if number <= 1:
        return [] if number == 0 else [[1]]
    partitions: list[list[int]] = []
    for n in range(1, slots + 1):
        if n == number:
            partitions.append([n])
        else:
            for partition in get_partitions_simple_recursion(number=number - n, slots=min(number - n, n),
                                                             safe_limit=safe_limit):
                partitions.append([n] + partition)
    for partition in partitions:
        assert sum(partition) == number, f'{partition=} {sum(partition)=} {number=}'
    return partitions


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def solve_counting_summations_p0076_s0(*, num: int) -> int:
    result: int = num_partitions_recursive_pentagonal(number=num) - 1
    return result


@register_solution(euler_problem=euler_problem, max_test_case_index=2, allow_max_override=False)
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def solve_counting_summations_p0076_s1(*, num: int) -> int:
    return num_partitions_simple_recursion(number=num, slots=num) - 1


@register_solution(euler_problem=euler_problem, max_test_case_index=1, allow_max_override=False)
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def solve_counting_summations_p0076_s2(*, num: int) -> int:
    return len(get_partitions_simple_recursion(number=num, slots=num)) - 1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
