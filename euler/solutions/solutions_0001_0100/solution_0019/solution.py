#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 19: Counting Sundays.

  Problem Statement:
    You are given the following information, but you may prefer to do some
    research for yourself.

    1 Jan 1900 was a Monday.

    Thirty days has September,
    April, June and November.
    All the rest have thirty-one,
    Saving February alone,
    Which has twenty-eight, rain or shine.
    And on leap years, twenty-nine.

    A leap year occurs on any year evenly divisible by 4, but not on a
    century unless it is divisible by 400.

    How many Sundays fell on the first of the month during the twentieth
    century (1 Jan 1901 to 31 Dec 2000)?

  Solution Approach:
    To solve this problem, begin by implementing a precise calendar algorithm
    that accounts for month lengths and leap years accurately as specified.
    Use the given fact that 1 Jan 1900 was a Monday as a starting point.
    Calculate the day of the week sequentially for each first day of the month
    from 1 Jan 1901 through 31 Dec 2000. Count each occurrence where the day
    is Sunday. This approach combines date calculation logic with iteration
    and conditional checks, requiring careful handling of leap years and
    month transitions to produce the correct count.

  Test Cases:
    main:
      end_year=2000,
      start_year=1901,
      answer=171.


  Answer: 171
  URL: https://projecteuler.net/problem=19
"""
from __future__ import annotations

from datetime import date

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=19, test_case_category=TestCaseCategory.EXTENDED)
def counting_sundays(*, end_year: int, start_year: int) -> int:
    return sum((date(y, m, day=1).isoweekday() == 7 for m in range(1, 13) for y in range(start_year, end_year + 1)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=19, time_out_in_seconds=300, mode='evaluate'))
