#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 76: counting_summations

Problem Statement:
  It is possible to write five as a sum in exactly six different ways:
  \begin{align} &4 + 1\\ &3 + 2\\ &3 + 1 + 1\\ &2 + 2 + 1\\ &2 + 1 + 1 + 1\\ &1 +
  1 + 1 + 1 + 1 \end{align} How many different ways can one hundred be written as
  a sum of at least two positive integers?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=76
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.integer_partitions import get_partitions, num_integer_partitions, num_partitions
from euler.setup import TestCase
from euler.sys_utils import set_resource_limits

test_cases: list[TestCase] = [
    TestCase(
        answer=6,
        is_main_case=False,
        kwargs={'num': 5},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=204225,
        is_main_case=False,
        kwargs={'num': 50},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=190569291,
        is_main_case=False,
        kwargs={'num': 100},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=24061467864032622473692149727990,
        is_main_case=False,
        kwargs={'num': 1000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #76
@register_solution(problem_number=76, test_cases=test_cases)
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def sol_1_counting_summations(*, num: int) -> int:
    """
    Count the number of ways to write a number as a sum of at least two positive integers.

    This solution addresses Project Euler problem 76 by calculating all possible ways to
    express 'num' as a sum of at least two positive integers. It subtracts 1 from the total
    number of partitions to exclude the trivial case of the number itself.

    Args:
        num: The target number to be expressed as a sum

    Returns:
        The count of different ways to express num as a sum of at least two positive integers

    Note:
        For large numbers, the function may encounter a recursion limit. In such cases, it
        dynamically increases the recursion limit to accommodate the calculation.
    """
    return num_partitions(number=num) - 1


# Register this function as a solution for problem #76
@register_solution(problem_number=76, test_cases=test_cases[:-1])
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def sol_2_counting_summations(*, num: int) -> int:
    """
    Count the number of ways to write a number as a sum of at least two positive integers.

    This solution addresses Project Euler problem 76 by calculating all possible ways to
    express 'num' as a sum of at least two positive integers. It subtracts 1 from the total
    number of partitions to exclude the trivial case of the number itself.

    Args:
        num: The target number to be expressed as a sum

    Returns:
        The count of different ways to express num as a sum of at least two positive integers

    Note:
        For large numbers, the function may encounter a recursion limit. In such cases, it
        dynamically increases the recursion limit to accommodate the calculation.
    """
    return num_integer_partitions(number=num, slots=num) - 1


# Register this function as a solution for problem #76
@register_solution(problem_number=76, test_cases=test_cases[:-2])
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def sol_3_counting_summations(*, num: int) -> int:
    """
    Count the number of ways to write a number as a sum of at least two positive integers.

    This solution addresses Project Euler problem 76 by calculating all possible ways to
    express 'num' as a sum of at least two positive integers. It subtracts 1 from the total
    number of partitions to exclude the trivial case of the number itself.

    Args:
        num: The target number to be expressed as a sum

    Returns:
        The count of different ways to express num as a sum of at least two positive integers

    Note:
        For large numbers, the function may encounter a recursion limit. In such cases, it
        dynamically increases the recursion limit to accommodate the calculation.
    """
    return len(get_partitions(number=num, slots=num)) - 1


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(76))
