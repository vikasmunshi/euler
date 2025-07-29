#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 19: counting_sundays

Problem Statement:
  You are given the following information, but you may prefer to do some research
  for yourself. 1 Jan 1900 was a Monday. Thirty days has September, April, June
  and November. All the rest have thirty-one, Saving February alone, Which has
  twenty-eight, rain or shine. And on leap years, twenty-nine. A leap year occurs
  on any year evenly divisible by 4, but not on a century unless it is divisible
  by 400. How many Sundays fell on the first of the month during the twentieth
  century (1 Jan 1901 to 31 Dec 2000)?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=19
Answer: None
"""
from __future__ import annotations

from datetime import date

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=171,
        is_main_case=False,
        kwargs={'end_year': 2000, 'start_year': 1901},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #19
@register_solution(problem_number=19, test_cases=test_cases)
def counting_sundays(*, end_year: int, start_year: int) -> int:
    """Count the number of Sundays that fall on the first day of the month in a given range of years.

    This function uses Python's datetime module to determine the day of the week for the
    first day of each month in the specified range of years. In the ISO calendar used by
    the datetime module, Monday is 1 and Sunday is 7.

    Implementation Details:
    1. We use a generator expression to create a sequence of all first-of-month dates
       within the specified year range.
    2. For each date, we check if it falls on a Sunday using the isoweekday() method.
    3. The sum() function counts all dates that satisfy the condition.

    The approach is concise and leverages Python's built-in libraries for date manipulation,
    avoiding the need to implement complex calendar calculations manually.

    Alternative Approaches:
    1. Manual Day-of-Week Calculation: One could implement Zeller's Congruence or similar
       formulas to determine the day of week without relying on the datetime module.
    2. Day Advancement: Starting from a known date (like 1 Jan 1900 = Monday), iteratively
       advance through all dates, tracking day of week and counting Sundays on the first.
    3. Calendar Module: Python's calendar module could also be used for similar functionality.

    Complexity Analysis:
    - Time Complexity: O(Y×M) where Y is the number of years and M is the number of months (12)
    - Space Complexity: O(1) as we only generate one date at a time in the generator expression

    Args:
        start_year: The first year to include in the count (inclusive)
        end_year: The last year to include in the count (inclusive)

    Returns:
        The count of Sundays that fall on the first day of any month in the range

    Example:
        >>> counting_sundays(start_year=1901, end_year=2000)
        171  # There are 171 Sundays falling on the first of a month in the 20th century
    """
    return sum(date(y, m, day=1).isoweekday() == 7 for m in range(1, 13) for y in range(start_year, end_year + 1))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(19))
