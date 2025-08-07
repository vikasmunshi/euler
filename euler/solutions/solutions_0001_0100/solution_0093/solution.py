#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 93: Arithmetic Expressions.

  Problem Statement:
    By using each of the digits from the set, {1, 2, 3, 4}, exactly once, and making
    use of the four arithmetic operations (+, -, x, /) and brackets/parentheses, it is
    possible to form different positive integer targets.

    For example,

        8 = (4 x (1 + 3)) / 2
        14 = 4 x (3 + 1 / 2)
        19 = 4 x (2 + 3) - 1
        36 = 3 x 4 x (2 + 1)

    Note that concatenations of the digits, like 12 + 34, are not allowed.

    Using the set, {1, 2, 3, 4}, it is possible to obtain thirty-one different
    target numbers of which 36 is the maximum, and each of the numbers 1 to 28 can
    be obtained before encountering the first non-expressible number.

    Find the set of four distinct digits, a < b < c < d, for which the longest set
    of consecutive positive integers, 1 to n, can be obtained, giving your answer
    as a string: abcd.

  Solution Approach:
    To solve this problem, start by generating all possible sets of four distinct
    digits from 1 to 9. For each set, compute all valid arithmetic expressions that
    can be formed using each digit exactly once, the four basic operations, and
    parentheses.

    Systematically evaluate these expressions to find all positive integers they
    produce. Then identify the longest consecutive sequence starting from 1 for
    each set of digits.

    Comparing these sequences across all digit sets will reveal the one with the
    longest run of consecutive positive integers. Employing recursion and
    permutation techniques will be effective for enumerating expressions and
    combinations efficiently.

  Test Cases:
    main:
      answer=1258.


  Answer: 1258
  URL: https://projecteuler.net/problem=93
"""
from __future__ import annotations

from functools import lru_cache
from typing import Set

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution


@lru_cache(maxsize=None)
def eval_all_operations(vals: tuple[int | float, ...]) -> Set[int | float]:
    if (len_v := len(vals)) == 1:
        return {vals[0]}
    s = set()
    for i in range(len_v - 1):
        for j in range(i + 1, len_v):
            a, b = (vals[i], vals[j])
            r = tuple([vals[k] for k in range(len_v) if k not in (i, j)])
            s |= eval_all_operations(r + (a + b,))
            s |= eval_all_operations(r + (abs(a - b),))
            s |= eval_all_operations(r + (a * b,))
            if b > 0:
                s |= eval_all_operations(r + (a / b,))
            if a > 0:
                s |= eval_all_operations(r + (b / a,))
    return s


@register_solution(euler_problem=93, test_case_category=TestCaseCategory.EXTENDED)
def arithmetic_expressions() -> str:
    max_digits: str = ''
    max_length: int = 0
    max_results: Set[int] = set()
    for a in range(1, 7):
        for b in range(a + 1, 8):
            for c in range(b + 1, 9):
                for d in range(c + 1, 10):
                    results: Set[int] = {int(x) for x in eval_all_operations((a, b, c, d)) if x.is_integer()}
                    length = 0
                    while length + 1 in results:
                        length += 1
                    if length > max_length:
                        max_length, max_digits, max_results = (length, f'{a}{b}{c}{d}', results)
    if show_solution():
        print(f'max_digits={max_digits!r} max_length={max_length!r} max_results={max_results!r}')
    return max_digits


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=93, time_out_in_seconds=300, mode='evaluate'))
