#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 584: Birthday Problem Revisited.

Problem Statement:
    A long long time ago in a galaxy far far away, the Wimwians, inhabitants of planet WimWi,
    discovered an unmanned drone that had landed on their planet. On examining the drone,
    they uncovered a device that sought the answer for the so called "Birthday Problem".

    If people on your planet were to enter a very large room one by one, what will be the
    expected number of people in the room when you first find 3 people with Birthdays within 1
    day from each other.

    The description further instructed them to enter the answer into the device and send the
    drone into space again. Startled by this turn of events, the Wimwians consulted their
    best mathematicians. Each year on Wimwi has 10 days and the mathematicians assumed equally
    likely birthdays and ignored leap years (leap years in Wimwi have 11 days), and found
    5.78688636 to be the required answer. As such, the Wimwians entered this answer and sent
    the drone back into space.

    After traveling light years away, the drone then landed on planet Joka. The same events
    ensued except this time, the numbers in the device had changed due to some unknown
    technical issues. The description read:

    If people on your planet were to enter a very large room one by one, what will be the
    expected number of people in the room when you first find 3 people with Birthdays within
    7 days from each other.

    With a 100-day year on the planet, the Jokars (inhabitants of Joka) found the answer to
    be 8.48967364 (rounded to 8 decimal places because the device allowed only 8 places after
    the decimal point) assuming equally likely birthdays. They too entered the answer into
    the device and launched the drone into space again.

    This time the drone landed on planet Earth. As before the numbers in the problem
    description had changed. It read:

    If people on your planet were to enter a very large room one by one, what will be the
    expected number of people in the room when you first find 4 people with Birthdays within
    7 days from each other.

    What would be the answer (rounded to eight places after the decimal point) the people of
    Earth have to enter into the device for a year with 365 days? Ignore leap years. Also
    assume that all birthdays are equally likely and independent of each other.

URL: https://projecteuler.net/problem=584
"""
from typing import Any

euler_problem: int = 584
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'year_length': 365, 'k': 4, 'day_range': 7}, 'answer': None},
]
encrypted: str = (
    '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'
    'vlKgqccBDYQNLor/GvANzA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
