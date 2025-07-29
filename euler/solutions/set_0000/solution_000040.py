#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 40: champernowne_s_constant

Problem Statement:
  An irrational decimal fraction is created by concatenating the positive
  integers: 0.12345678910{\color{red}\mathbf 1}112131415161718192021\cdots It can
  be seen that the 12th digit of the fractional part is 1. If d_n represents the
  nth digit of the fractional part, find the value of the following expression.
  d_1 * d_{10} * d_{100} * d_{1000} * d_{10000} * d_{100000} * d_{1000000}

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=40
Answer: None
"""
from __future__ import annotations

from functools import reduce

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase


def get_nth_digit_champernowne_s_constant(n: int) -> int:
    """
    Calculate the nth digit of Champernowne's constant.

    This helper function efficiently determines which digit appears at the
    specified position in Champernowne's constant without generating the entire sequence.

    Args:
        n: The position of the digit to find (1-indexed)

    Returns:
        The digit at the nth position as an integer

    Example:
        >>> get_nth_digit_champernowne_s_constant(12)
        1  # The 12th digit in the sequence is 1
        >>> get_nth_digit_champernowne_s_constant(1)
        1  # The 1st digit is 1
        >>> get_nth_digit_champernowne_s_constant(10)
        1  # The 10th digit is 1 (from the number 10)
    """
    length_till_num_digits, length_with_num_digits, num_digits = 0, 0, 0
    while length_with_num_digits < n:
        num_digits += 1
        length_till_num_digits = length_with_num_digits
        length_with_num_digits += num_digits * 9 * 10 ** (num_digits - 1)

    offset_of_number = n - length_till_num_digits - 1
    digit_in_number = offset_of_number % num_digits
    number = 10 ** (num_digits - 1) + offset_of_number // num_digits
    return int(str(number)[digit_in_number])


test_cases: list[TestCase] = [
    TestCase(
        answer=1,
        is_main_case=False,
        kwargs={'i': 1},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=5,
        is_main_case=False,
        kwargs={'i': 2},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=15,
        is_main_case=False,
        kwargs={'i': 3},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=105,
        is_main_case=False,
        kwargs={'i': 4},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=210,
        is_main_case=False,
        kwargs={'i': 5},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=210,
        is_main_case=False,
        kwargs={'i': 6},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=1470,
        is_main_case=False,
        kwargs={'i': 7},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=11760,
        is_main_case=False,
        kwargs={'i': 8},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=11760,
        is_main_case=False,
        kwargs={'i': 9},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=11760,
        is_main_case=False,
        kwargs={'i': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=0,
        is_main_case=False,
        kwargs={'i': 11},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #40
@register_solution(problem_number=40, test_cases=test_cases)
def champernowne_s_constant(*, i: int) -> int:
    """
    Calculate the product of specific digits in Champernowne's constant.

    This solution finds the product of digits at positions 10^0, 10^1, 10^2, ..., 10^i
    in Champernowne's constant (0.123456789101112...) without generating the
    entire sequence. It uses efficient position calculations to find each digit.

    Args:
        i: The maximum exponent to consider (inclusive).
           For the original problem, i=6 to get positions 1, 10, 100, ..., 1,000,000

    Returns:
        The product of the digits at the specified positions

    Example:
        >>> champernowne_s_constant(i=6)
        210  # Product of digits at positions 1, 10, 100, 1000, 10000, 100000, 1000000
        >>> champernowne_s_constant(i=2)
        5    # Product of digits at positions 1, 10, 100
    """
    return reduce(lambda x, y: x * y, (get_nth_digit_champernowne_s_constant(10 ** i) for i in range(0, i + 1)), 1)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(40))
