#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 31: coin_sums

Problem Statement:
  In the United Kingdom the currency is made up of pound (£) and pence (p). There
  are eight coins in general circulation: 1p, 2p, 5p, 10p, 20p, 50p, £1 (100p),
  and £2 (200p). It is possible to make £2 in the following way: 1×£1 + 1×50p +
  2×20p + 1×5p + 1×2p + 3×1p How many different ways can £2 be made using any
  number of coins?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=31
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=1,
        is_main_case=False,
        kwargs={'coins': [1, 2, 5, 10, 20, 50, 100, 200], 'target': 0},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=73682,
        is_main_case=False,
        kwargs={'coins': [1, 2, 5, 10, 20, 50, 100, 200], 'target': 200},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=321335886,
        is_main_case=False,
        kwargs={'coins': [1, 2, 5, 10, 20, 50, 100, 200], 'target': 1000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=10056050940818192726001,
        is_main_case=False,
        kwargs={'coins': [1, 2, 5, 10, 20, 50, 100, 200], 'target': 100000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #31
@register_solution(problem_number=31, test_cases=test_cases)
def coin_sums(*, coins: list, target: int) -> int:
    """Calculate the number of different ways to make a target amount using given coin denominations.

    This function implements a dynamic programming solution to the coin change problem,
    counting all possible combinations of coins that sum up to the target amount.

    Args:
        target: The target amount to make
        coins: A tuple of available coin denominations (default: UK coins in pence)

    Returns:
        The number of different ways to make the target amount using the given coins

    Example:
        >>> coin_sums(target=5, coins=(1, 2, 5))
        4  # The ways are: [1,1,1,1,1], [1,1,1,2], [1,2,2], and [5]
        >>> coin_sums(target=200)
        73682  # Number of ways to make £2 using standard UK coins
    """
    result = [1] + [0] * target
    for coin in coins:
        for i in range(coin, target + 1):
            result[i] += result[i - coin]
    return result[-1]


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(31))
