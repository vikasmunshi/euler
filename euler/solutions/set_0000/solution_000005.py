#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 5: smallest_multiple

Problem Statement:
  2520 is the smallest number that can be divided by each of the numbers from 1 to
  10 without any remainder. What is the smallest positive number that is evenly
  divisibledivisible with no remainder by all of the numbers from 1 to 20?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=5
Answer: None
"""
from __future__ import annotations

from functools import reduce
from math import gcd

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=2520,
        is_main_case=False,
        kwargs={'n': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=232792560,
        is_main_case=False,
        kwargs={'n': 20},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=3099044504245996706400,
        is_main_case=False,
        kwargs={'n': 50},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=69720375229712477164533808935312303556800,
        is_main_case=False,
        kwargs={'n': 100},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #5
@register_solution(problem_number=5, test_cases=test_cases)
def smallest_multiple(*, n: int) -> int:
    """Calculate the smallest positive number divisible by all integers from 1 to n.

    This function computes the least common multiple (LCM) of all integers from 1 to n.
    It uses the mathematical property that LCM(a,b) = (a*b)/gcd(a,b) and extends it
    to multiple numbers using the reduce function.

    Args:
        n (int): The upper limit of the range of integers to consider.
            Must be a positive integer.

    Returns:
        int: The smallest positive number that is evenly divisible by all
            integers from 1 to n.

    Time Complexity: O(n log n) - iterating through n numbers with gcd calculation
    Space Complexity: O(1) - uses constant extra space regardless of input size
    """
    return reduce(lambda x, y: x * y // gcd(x, y), range(2, n + 1), 1)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(5))
