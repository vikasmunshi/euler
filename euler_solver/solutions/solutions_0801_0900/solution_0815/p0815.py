#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 815: Group by Value.

Problem Statement:
    A pack of cards contains 4n cards with four identical cards of each value.
    The pack is shuffled and cards are dealt one at a time and placed in piles
    of equal value. If the card has the same value as any pile it is placed in
    that pile. If there is no pile of that value then it begins a new pile.
    When a pile has four cards of the same value it is removed.

    Throughout the process the maximum number of non empty piles is recorded.
    Let E(n) be its expected value. You are given E(2) = 1.97142857 rounded to
    8 decimal places.

    Find E(60). Give your answer rounded to 8 digits after the decimal point.

URL: https://projecteuler.net/problem=815
"""
from typing import Any

euler_problem: int = 815
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 60}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
