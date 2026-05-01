#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 641: A Long Row of Dice.

Problem Statement:
    Consider a row of n dice all showing 1.

    First turn every second die, (2,4,6,...) so that the number showing is
    increased by 1. Then turn every third die. The sixth die will now show a 3.
    Then turn every fourth die and so on until every nth die (only the last die)
    is turned. If the die to be turned is showing a 6 then it is changed to show a 1.

    Let f(n) be the number of dice that are showing a 1 when the process finishes.
    You are given f(100)=2 and f(10^8) = 69.

    Find f(10^36).

URL: https://projecteuler.net/problem=641
"""
from typing import Any

euler_problem: int = 641
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000000000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'onL1lXIrufMuN4Sn'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
