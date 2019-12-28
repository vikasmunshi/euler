#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=19
You are given the following information, but you may prefer to do some research for yourself.

1 Jan 1900 was a Monday.
Thirty days has September,
April, June and November.
All the rest have thirty-one,
Saving February alone,
Which has twenty-eight, rain or shine.
And on leap years, twenty-nine.
A leap year occurs on any year evenly divisible by 4, but not on a century unless it is divisible by 400.
How many Sundays fell on the first of the month during the twentieth century (1 Jan 1901 to 31 Dec 2000)?
Answer: 171
"""
from datetime import date


def sundays_on_first_of_month(start_year: int, end_year: int) -> int:
    return sum(date(y, m, 1).isoweekday() == 7 for m in range(1, 13) for y in range(start_year, end_year + 1))


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate(sundays_on_first_of_month)(start_year=1901, end_year=2000, answer=171)
