#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0019/p0019.py :: solve_counting_sundays_p0019_s0.

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
URL: https://projecteuler.net/problem=19"""
from __future__ import annotations

from datetime import date


def solve(*, end_year: int, start_year: int) -> int:
    return sum((date(y, m, day=1).isoweekday() == 7 for m in range(1, 13) for y in range(start_year, end_year + 1)))


if __name__ == '__main__':
    import sys

    print(solve(end_year=int(sys.argv[1]), start_year=int(sys.argv[2])))
