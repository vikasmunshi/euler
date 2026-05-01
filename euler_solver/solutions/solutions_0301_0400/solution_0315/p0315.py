#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 315: Digital Root Clocks.

Problem Statement:
    Sam and Max are asked to transform two digital clocks into two "digital
    root" clocks. A digital root clock displays all intermediate values while
    repeatedly summing the digits until a single-digit result is reached.
    For example, input 137 is shown as: 137 -> 11 -> 2.

    Each decimal digit is shown on a seven-segment style panel: three
    horizontal segments (top, middle, bottom) and four vertical segments
    (top-left, top-right, bottom-left, bottom-right). A segment transition
    (turning a single segment on or off) consumes energy. For example, turning
    on a "2" costs 5 transitions, while a "7" costs 4.

    Sam's clock: for each displayed intermediate number the whole panel is
    turned on for that number, then the whole panel is turned off; each
    display costs twice the number of segments lit for that number.

    Max's clock: between successive numbers the clock changes only those
    segments that differ; it does not turn the entire panel off between steps.
    Thus energy equals transitions to reach the first display, plus the
    transitions between successive displays, plus the transitions to turn off
    the final single-digit display.

    The clocks are fed all prime numbers between A = 10^7 and B = 2*10^7.
    Find the difference between the total transitions required by Sam's clock
    and the total transitions required by Max's clock.

URL: https://projecteuler.net/problem=315
"""
from typing import Any

euler_problem: int = 315
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'min_limit': 10, 'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'min_limit': 10000000, 'max_limit': 20000000}, 'answer': None},
    {'category': 'extra', 'input': {'min_limit': 20000000, 'max_limit': 30000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
