#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 92: Square Digit Chains.

  Problem Statement:
    A number chain is created by continuously adding the square of the digits
    in a number to form a new number until it has been seen before.

    For example,

    44 -> 32 -> 13 -> 10 -> 1 -> 1
    85 -> 89 -> 145 -> 42 -> 20 -> 4 -> 16 -> 37 -> 58 -> 89

    Therefore any chain that arrives at 1 or 89 will become stuck in an
    endless loop. What is most amazing is that EVERY starting number will
    eventually arrive at 1 or 89.

    How many starting numbers below ten million will arrive at 89?

  Solution Approach:
    To solve this problem, implement a function that generates the number
    chain by repeatedly replacing a number with the sum of the squares of its
    digits. Use memoization to store results for numbers already processed to
    avoid redundant calculations and speed up the solution.

    Iterate through all starting numbers below ten million, applying the
    chain function to determine if the chain ends at 89. Count and return the
    number of such starting numbers. Understanding properties of these chains
    and efficient caching techniques are crucial for handling the problem
    efficiently.

  Test Cases:
    preliminary:
      power_of_10=2,
      answer=80.

      power_of_10=3,
      answer=857.

      power_of_10=4,
      answer=8558.

      power_of_10=5,
      answer=85623.

      power_of_10=6,
      answer=856929.

    main:
      power_of_10=7,
      answer=8581146.

    extended:
      power_of_10=8,
      answer=85744333.

      power_of_10=9,
      answer=854325192.


  Answer: 8581146
  URL: https://projecteuler.net/problem=92
"""
from __future__ import annotations

from typing import Dict

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution


@register_solution(euler_problem=92, test_case_category=TestCaseCategory.EXTENDED)
def square_digit_chains(*, power_of_10: int) -> int:
    a, sq, is89 = ([1], [x ** 2 for x in range(1, 10)], [False])
    results: Dict[int, int] = {}
    for n in range(1, power_of_10 + 1):
        b, a = (a, a + [0] * 81)
        is89 += map(terminates_in_89, range(len(b), len(a)))
        for i, v in enumerate(b):
            for s in sq:
                a[i + s] += v
        results[n] = sum((a[i] for i in range(len(a)) if is89[i]))
    if show_solution():
        print(f'Results for power_of_10={power_of_10}: {results}')
    return results[power_of_10]


def terminates_in_89(n: int) -> bool:
    while n != 1 and n != 89:
        n, t = (0, n)
        while t:
            n, t = (n + (t % 10) ** 2, t // 10)
    return n == 89


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=92, time_out_in_seconds=300, mode='evaluate'))
