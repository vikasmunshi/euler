#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 63: Powerful Digit Counts.

  Problem Statement:
    The 5-digit number, 16807=7 x 5, is also a fifth power. Similarly, the
    9-digit number, 134217728=8 x 9, is a ninth power.

    How many n-digit positive integers exist which are also an nth power?

  Solution Approach:
    To solve this problem, consider the relationship between the number of digits
    of a number and its value as a power. For an integer base b and exponent n,
    the number b^n will have a certain number of digits that can be determined
    using logarithms (specifically, using the formula floor(n * log10(b)) + 1).

    The task is to count all cases where the number of digits of b^n equals n.
    Start by iterating through possible bases and exponents, calculating the
    digit count of each power. Then compare the digit count to the exponent.
    Efficiently implement a stopping condition to avoid unnecessary computations
    when numbers exceed or fall below the required digit length.

    This approach combines mathematical insight on digit length with algorithmic
    iteration and conditional checks, enabling the counting of all n-digit nth powers.

  Test Cases:
    main:
      answer=49.


  Answer: 49
  URL: https://projecteuler.net/problem=63
"""
from __future__ import annotations

from math import ceil
from typing import Tuple

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution


@register_solution(euler_problem=63, test_case_category=TestCaseCategory.EXTENDED)
def powerful_digit_counts() -> int:
    result: int = 0
    n: int = 1
    while (solutions := n_digit_nth_powers(n)):
        result += len(solutions)
        n += 1
        if show_solution():
            print(f'n={n!r} len(solutions)={len(solutions)!r} solutions={solutions!r} ')
    return result


def n_digit_nth_powers(n: int) -> Tuple[int, ...]:
    start_range: int = ceil((10 ** (n - 1)) ** (1 / n))
    stop_range: int = ceil((10 ** n - 1) ** (1 / n)) + 1
    return tuple((r for i in range(start_range, stop_range) if len(str((r := (i ** n)))) == n))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=63, time_out_in_seconds=300, mode='evaluate'))
