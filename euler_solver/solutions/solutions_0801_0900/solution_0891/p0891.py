#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 891: Ambiguous Clock.

Problem Statement:
    A round clock only has three hands: hour, minute, second. All hands look
    identical and move continuously. Moreover, there is no number or reference
    mark so that the "upright position" is unknown. The clock functions the
    same as a normal 12-hour analogue clock.

    Despite the inconvenient design, for most time it is possible to tell the
    correct time (within a 12-hour cycle) from the clock, just by measuring
    accurately the angles between the hands. For example, if all three hands
    coincide, then the time must be 12:00:00.

    Nevertheless, there are several moments where the clock shows an ambiguous
    reading. For example, the following moment could be either 1:30:00 or
    7:30:00 (with the clock rotated 180 degrees). Thus both 1:30:00 and 7:30:00
    are ambiguous moments.
    Note that even if two hands perfectly coincide, we can still see them as two
    distinct hands in the same position. Thus for example 3:00:00 and 9:00:00
    are not ambiguous moments.

    How many ambiguous moments are there within a 12-hour cycle?

URL: https://projecteuler.net/problem=891
"""
from typing import Any

euler_problem: int = 891
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
