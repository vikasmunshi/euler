#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 31: Coin sums

Problem Statement:
In the United Kingdom the currency is made up of pound (£) and pence (p). There are eight coins in general circulation:
1p, 2p, 5p, 10p, 20p, 50p, £1 (100p), and £2 (200p).

It is possible to make £2 in the following way:
1×£1 + 1×50p + 2×20p + 1×5p + 1×2p + 3×1p

How many different ways can £2 be made using any number of coins?

Solution Approach:
This solution uses dynamic programming to solve the coin change problem. The implementation
creates a table where each cell represents the number of ways to make a specific amount
using the available coins.

The algorithm works as follows:
1. Initialize an array with 1 way to make 0 (using no coins) and 0 ways for all other amounts
2. For each coin denomination, update the ways to make each amount from the coin value up to target
3. Each cell [i] represents the number of ways to make amount i using all coins considered so far

This bottom-up approach builds the solution incrementally, reusing previously calculated results
to find the total number of ways to make the target amount.

Test Cases:
- For target=0, the answer is 1 (only one way: use no coins)
- For target=200 (£2), the answer is 73,682
- For target=1000, the answer is 321,335,886
- For larger targets like 100000, the algorithm remains efficient

URL: https://projecteuler.net/problem=31
Answer: 73682
"""
from typing import Tuple

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=31)
problem_number: int = 31

COINS: Tuple[int, ...] = (1, 2, 5, 10, 20, 50, 100, 200)

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'target': 0, 'coins': COINS}, answer=1, ),
    ProblemArgs(kwargs={'target': 200, 'coins': COINS}, answer=73682, ),
    ProblemArgs(kwargs={'target': 1000, 'coins': COINS}, answer=321335886, ),
    ProblemArgs(kwargs={'target': 100000, 'coins': COINS}, answer=10056050940818192726001, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def coin_sum(*, target: int, coins: Tuple[int, ...]) -> int:
    """Calculate the number of different ways to make a target amount using given coin denominations.

    This function implements a dynamic programming solution to the coin change problem,
    counting all possible combinations of coins that sum up to the target amount.

    Args:
        target: The target amount to make
        coins: A tuple of available coin denominations (default: UK coins in pence)

    Returns:
        The number of different ways to make the target amount using the given coins

    Example:
        >>> coin_sum(target=5, coins=(1, 2, 5))
        4  # The ways are: [1,1,1,1,1], [1,1,1,2], [1,2,2], and [5]
        >>> coin_sum(target=200)
        73682  # Number of ways to make £2 using standard UK coins
    """
    result = [1] + [0] * target
    for coin in coins:
        for i in range(coin, target + 1):
            result[i] += result[i - coin]
    return result[-1]


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
