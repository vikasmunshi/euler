#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 55: lychrel_numbers

Problem Statement:
  If we take 47, reverse and add, 47 + 74 = 121, which is palindromic. Not all
  numbers produce palindromes so quickly. For example, \begin{align} 349 + 943 &=
  1292\\ 1292 + 2921 &= 4213\\ 4213 + 3124 &= 7337 \end{align} That is, 349 took
  three iterations to arrive at a palindrome. Although no one has proved it yet,
  it is thought that some numbers, like 196, never produce a palindrome. A number
  that never forms a palindrome through the reverse and add process is called a
  Lychrel number. Due to the theoretical nature of these numbers, and for the
  purpose of this problem, we shall assume that a number is Lychrel until proven
  otherwise. In addition you are given that for every number below ten-thousand,
  it will either (i) become a palindrome in less than fifty iterations, or, (ii)
  no one, with all the computing power that exists, has managed so far to map it
  to a palindrome. In fact, 10677 is the first number to be shown to require over
  fifty iterations before producing a palindrome: 4668731596684224866951378664 (53
  iterations, 28-digits). Surprisingly, there are palindromic numbers that are
  themselves Lychrel numbers; the first example is 4994. How many Lychrel numbers
  are there below ten-thousand? NOTE: Wording was modified slightly on 24 April
  2007 to emphasise the theoretical nature of Lychrel numbers.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=55
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=249,
        is_main_case=False,
        kwargs={'max_iterations': 50, 'max_limit': 10000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #55
@register_solution(problem_number=55, test_cases=test_cases)
def lychrel_numbers(*, max_iterations: int, max_limit: int) -> int:
    """
    Count the number of Lychrel numbers below a given limit.

    This solution identifies Lychrel numbers by applying the reverse-and-add process for each
    number from 1 to max_limit. If a number doesn't form a palindrome within max_iterations,
    it is considered a Lychrel number for the purpose of this problem.

    Args:
        max_limit: The upper limit (inclusive) for finding Lychrel numbers
        max_iterations: The maximum number of reverse-and-add iterations to perform
                        before considering a number to be Lychrel

    Returns:
        The count of Lychrel numbers below max_limit

    Example:
        >>> lychrel_numbers(max_limit=10000, max_iterations=50)
        249
    """
    return sum(is_lychrel(number=i, max_iterations=max_iterations) for i in range(1, max_limit + 1))


def is_lychrel(*, number: int, max_iterations: int) -> bool:
    """Determine if a number is a Lychrel number.

    A Lychrel number is a number that never forms a palindrome through the iterative
    process of reversing its digits and adding to the original number. For the purpose
    of this problem, a number is considered Lychrel if it doesn't produce a palindrome
    within the specified maximum number of iterations.

    Args:
        number: The number to test for being a Lychrel number.
        max_iterations: The maximum number of reverse-and-add iterations to perform.

    Returns:
        True if the number is a Lychrel number (doesn't form a palindrome within
        the specified iterations), False otherwise.

    Examples:
        >>> is_lychrel(number=196, max_iterations=50)
        True  # 196 is thought to be a Lychrel number
        >>> is_lychrel(number=47, max_iterations=50)
        False  # 47 becomes palindromic after just one iteration
    """
    for _ in range(max_iterations):
        number += int(str(number)[::-1])
        if str(number) == str(number)[::-1]:
            return False
    else:
        return True


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(55))
