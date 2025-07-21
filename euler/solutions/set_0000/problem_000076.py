# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 76:

Problem Statement:
It is possible to write five as a sum in exactly six different ways:

4 + 1
3 + 2
3 + 1 + 1
2 + 2 + 1
2 + 1 + 1 + 1
1 + 1 + 1 + 1 + 1

How many different ways can one hundred be written as a sum of at least two positive integers?

Solution Approach:
This solution uses a recursive approach with memoization to solve the integer partition problem.
An integer partition of a number n is a way of writing n as a sum of positive integers.

The algorithm uses dynamic programming with a recursive function that:
1. Computes the number of ways to partition 'number' using integers no larger than 'slots'.
2. Uses lru_cache for memoization to avoid redundant calculations and improve performance.
3. Handles base cases (number = 0 returns 0, number = 1 returns 1).
4. For other cases, it recursively computes the sum of partitions where each partition starts with a
   number n (1 ≤ n ≤ slots).
5. The recursion is implemented through the formula:
   num_partitions(number, slots) = ∑ num_partitions(number-n, min(number-n, n)) for n in range(1, slots+1)
6. Handles recursion limits for large numbers by dynamically adjusting the recursion limit as needed.

The result is decremented by 1 to exclude the partition that contains only the number itself,
since the problem asks for sums of at least two positive integers.

Test Cases:

URL: https://projecteuler.net/problem=76
Answer:
"""

from euler.evaluator import evaluate_solutions, register_solution
from euler.sys_utils import set_resource_limits
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.integer_partitions import get_partitions, num_integer_partitions, num_partitions

# The problem number from Project Euler (https://projecteuler.net/problem=76)
problem_number: int = 76

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'num': 5}, answer=6, ),
    ProblemArgs(kwargs={'num': 50}, answer=204225, ),
    ProblemArgs(kwargs={'num': 100}, answer=190569291, ),
    ProblemArgs(kwargs={'num': 1000}, answer=24061467864032622473692149727990, ),
]


# Register this function as a solution for problem #76 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def count_partitions(*, num: int) -> int:
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


# Register this function as a solution for problem #76 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list[:-1])
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def count_integer_partitions(*, num: int) -> int:
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


# Register this function as a solution for problem #76 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list[:-2])
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def list_integer_partitions(*, num: int) -> int:
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
    raise SystemExit(evaluate_solutions(problem_number))
