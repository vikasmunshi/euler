#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 645: Every Day Is a Holiday.

Problem Statement:
    On planet J, a year lasts for D days. Holidays are defined by the two following
    rules.

        1. At the beginning of the reign of the current Emperor, his birthday is
           declared a holiday from that year onwards.
        2. If both the day before and after a day d are holidays, then d also becomes
           a holiday.

    Initially there are no holidays. Let E(D) be the expected number of Emperors to
    reign before all the days of the year are holidays, assuming that their birthdays
    are independent and uniformly distributed throughout the D days of the year.

    You are given E(2)=1, E(5)=31/6, E(365) approximately 1174.3501.

    Find E(10000). Give your answer rounded to 4 digits after the decimal point.

URL: https://projecteuler.net/problem=645
"""
from typing import Any

euler_problem: int = 645
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
    '0xdrvCam/wZ9Nm8gPTjbt7YNj57KP7WJFYtRfQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
