#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 25:  1000 Digit Fibonacci Number.

  Problem Statement:
    The Fibonacci sequence is defined by the recurrence relation:

        F_n = F_{n - 1} + F_{n - 2}, where F_1 = 1 and F_2 = 1.

    Hence the first 12 terms will be:

        F_1 = 1
        F_2 = 1
        F_3 = 2
        F_4 = 3
        F_5 = 5
        F_6 = 8
        F_7 = 13
        F_8 = 21
        F_9 = 34
        F_10 = 55
        F_11 = 89
        F_12 = 144

    The 12th term, F_12, is the first term to contain three digits.

    What is the index of the first term in the Fibonacci sequence to contain 1000 digits?

  Solution Approach:
    To solve this problem, you can use the properties of the Fibonacci sequence
    and numerical methods. The key idea is to find the smallest index n such
    that the Fibonacci number F_n has at least 1000 digits. Directly computing
    Fibonacci numbers for large n by naive methods may be inefficient.

    A more efficient approach involves either:

    1. Using an iterative or dynamic programming technique to generate Fibonacci
    numbers until one reaches 1000 digits.

    2. Applying Binet's formula approximation and logarithms to estimate n by
    solving for the term's number of digits.

    Both methods require handling large integers or floating-point precision
    carefully. Efficient libraries or built-in big integer support in your
    programming language can help to handle large Fibonacci numbers.

  Test Cases:
    preliminary:
      n=3,
      answer=12.

    main:
      n=1000,
      answer=4782.


  Answer: 4782
  URL: https://projecteuler.net/problem=25
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=25, test_case_category=TestCaseCategory.EXTENDED)
def solution_1000_digit_fibonacci_number(*, n: int) -> int:
    a, b = (1, 1)
    i = 2
    while b < 10 ** (n - 1):
        a, b = (b, a + b)
        i += 1
    return i


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=25, time_out_in_seconds=300, mode='evaluate'))
