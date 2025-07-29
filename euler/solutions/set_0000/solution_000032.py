#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 32: pandigital_products

Problem Statement:
  We shall say that an n-digit number is pandigital if it makes use of all the
  digits 1 to n exactly once; for example, the 5-digit number, 15234, is 1 through
  5 pandigital. The product 7254 is unusual, as the identity, 39 * 186 = 7254,
  containing multiplicand, multiplier, and product is 1 through 9 pandigital. Find
  the sum of all products whose multiplicand/multiplier/product identity can be
  written as a 1 through 9 pandigital. HINT: Some products can be obtained in more
  than one way so be sure to only include it once in your sum.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=32
Answer: None
"""
from __future__ import annotations

from itertools import permutations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=45228,
        is_main_case=False,
        kwargs={},
        solution_execution_time=None,
        solved=False
    ),
]

digits = ('1', '2', '3', '4', '5', '6', '7', '8', '9')


# Register this function as a solution for problem #32
@register_solution(problem_number=32, test_cases=test_cases)
def pandigital_products() -> int:
    """Calculate the sum of all products whose multiplicand/multiplier/product identity is 1-9 pandigital.

    A pandigital product identity is an equation a × b = c where the digits used in a, b, and c
    together use each digit from 1-9 exactly once.

    Returns:
        The sum of all unique products that can be written as part of a 1-9 pandigital identity

    Example:
        >>> pandigital_products()
        45228  # Includes products like 7254 from 39 × 186
    """
    return sum(set(
        c
        for a_len, b_len in ((1, 4), (2, 3))
        for a in permutations(digits, a_len)
        for b in permutations((d for d in digits if d not in a), b_len)
        if ''.join(sorted((a_str := ''.join(a)) + (b_str := ''.join(b)) + str(c := (int(a_str) * int(b_str)))))
        == '123456789'))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(32))
