#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 19: Counting Sundays.

Problem Statement:
    You are given the following information, but you may prefer to do some research
    for yourself.

    1 Jan 1900 was a Monday.
    Thirty days has September,
    April, June and November.
    All the rest have thirty-one,
    Saving February alone,
    Which has twenty-eight, rain or shine.
    And on leap years, twenty-nine.
    A leap year occurs on any year evenly divisible by 4, but not on a century unless
    it is divisible by 400.

    How many Sundays fell on the first of the month during the twentieth century
    (1 Jan 1901 to 31 Dec 2000)?

Solution Approach:
    Use date arithmetic or simulate the calendar day-by-day or month-by-month.
    Count Sundays occurring on the 1st of each month between given dates.
    Use rules for leap years and month lengths for accurate counting.
    Time complexity is linear in the number of months, very efficient.

Answer: 171
URL: https://projecteuler.net/problem=19
"""
from __future__ import annotations

from datetime import date
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 19
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'end_year': 2000, 'start_year': 1901}, 'answer': 171},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_counting_sundays_p0019_s0(*, end_year: int, start_year: int) -> int:
    return sum((date(y, m, day=1).isoweekday() == 7 for m in range(1, 13) for y in range(start_year, end_year + 1)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
