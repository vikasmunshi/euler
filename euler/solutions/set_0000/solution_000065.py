#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 65: convergents_of_e

Problem Statement:
  The square root of 2 can be written as an infinite continued fraction. \sqrt{2}
  = 1 + \dfrac{1}{2 + \dfrac{1}{2 + \dfrac{1}{2 + \dfrac{1}{2 + ...}}}} The
  infinite continued fraction can be written, \sqrt{2} = [1; (2)], (2) indicates
  that 2 repeats ad infinitum. In a similar way, \sqrt{23} = [4; (1, 3, 1, 8)]. It
  turns out that the sequence of partial values of continued fractions for square
  roots provide the best rational approximations. Let us consider the convergents
  for \sqrt{2}. \begin{align} &1 + \dfrac{1}{2} = \dfrac{3}{2} \\ &1 + \dfrac{1}{2
  + \dfrac{1}{2}} = \dfrac{7}{5}\\ &1 + \dfrac{1}{2 + \dfrac{1}{2 + \dfrac{1}{2}}}
  = \dfrac{17}{12}\\ &1 + \dfrac{1}{2 + \dfrac{1}{2 + \dfrac{1}{2 +
  \dfrac{1}{2}}}} = \dfrac{41}{29} \end{align} Hence the sequence of the first ten
  convergents for \sqrt{2} are: 1, \dfrac{3}{2}, \dfrac{7}{5}, \dfrac{17}{12},
  \dfrac{41}{29}, \dfrac{99}{70}, \dfrac{239}{169}, \dfrac{577}{408},
  \dfrac{1393}{985}, \dfrac{3363}{2378}, ... What is most surprising is that the
  important mathematical constant,e = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, ... , 1, 2k,
  1, ...]. The first ten terms in the sequence of convergents for e are: 2, 3,
  \dfrac{8}{3}, \dfrac{11}{4}, \dfrac{19}{7}, \dfrac{87}{32}, \dfrac{106}{39},
  \dfrac{193}{71}, \dfrac{1264}{465}, \dfrac{1457}{536}, ... The sum of digits in
  the numerator of the 10th convergent is 1 + 4 + 5 + 7 = 17. Find the sum of
  digits in the numerator of the 100th convergent of the continued fraction for e.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=65
Answer: None
"""
from __future__ import annotations

from fractions import Fraction

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.sum_digits import sum_digits
from euler.setup import TestCase
from euler.sys_utils import set_resource_limits


def e_denominator(n: int) -> int:
    """Calculate the nth denominator in the continued fraction expansion of e.

    This function implements the pattern for the continued fraction expansion of e,
    which follows [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, ...] where every third term is 2k
    (with k increasing by 1 each cycle), and all other terms are 1.

    Args:
        n: The position in the continued fraction expansion (1-indexed)

    Returns:
        The value of the nth term in e's continued fraction expansion

    Examples:
        >>> e_denominator(1)  # First term
        2
        >>> e_denominator(2)  # Second term
        1
        >>> e_denominator(3)  # Third term
        2
        >>> e_denominator(6)  # Sixth term
        4
    """
    if n == 1:
        return 2
    elif n % 3 == 0:
        return 2 * n // 3
    else:
        return 1


def nth_convergent_of_e(n: int, *, _n: int = 1) -> Fraction | int:
    """Recursively calculate the nth convergent of the continued fraction of e.

    This function uses a recursive approach to compute the continued fraction convergent,
    working from the deepest level of the fraction back to the outermost level. It builds
    the fraction representation using the pattern of denominators for e.

    The implementation uses tail recursion, working from the first term (at the outermost level)
    toward the nth term, then building the fraction back up as the recursion unwinds.

    Args:
        n: The convergent number to calculate (1-indexed)
        _n: Internal parameter for tracking the current position during recursion (default=1)

    Returns:
        The nth convergent of e as a Fraction object (or int for n=1)

    Implementation Notes:
        - Uses the e_den function to determine the value at each position
        - The recursion terminates when __n reaches n (the target convergent)
        - Python's Fraction class handles the rational arithmetic automatically

    """
    if n == _n:
        return e_denominator(_n)
    return e_denominator(_n) + Fraction(1, nth_convergent_of_e(n, _n=_n + 1))


test_cases: list[TestCase] = [
    TestCase(
        answer=17,
        is_main_case=False,
        kwargs={'convergent_num': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=272,
        is_main_case=False,
        kwargs={'convergent_num': 100},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=4034,
        is_main_case=False,
        kwargs={'convergent_num': 1000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=55322,
        is_main_case=False,
        kwargs={'convergent_num': 10000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #65
@register_solution(problem_number=65, test_cases=test_cases)
@set_resource_limits(recursion_var='convergent_num', multiplier=1, set_int_max_str=True, when='always')
def convergents_of_e(*, convergent_num: int) -> int:
    """Calculate the sum of digits in the numerator of the nth convergent of e.

    This function computes the nth convergent of the continued fraction expansion of e,
    extracts its numerator, and returns the sum of the digits in that numerator.

    The solution leverages the recursive nth_convergent_of_e function to generate the
    continued fraction convergent, and the utility function sum_digits to efficiently
    compute the digit sum.

    Args:
        convergent_num: The convergent number to calculate (1-indexed)

    Returns:
        The sum of digits in the numerator of the nth convergent

    Examples:
        >>> convergents_of_e(convergent_num=10)
        17  # The numerator is 1457, and 1+4+5+7=17

        >>> convergents_of_e(convergent_num=100)
        272  # The sum of digits in the numerator of the 100th convergent
    """
    return sum_digits(nth_convergent_of_e(convergent_num).numerator)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(65))
