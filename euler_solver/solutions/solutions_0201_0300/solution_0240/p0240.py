#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 240: Top Dice.

Problem Statement:
    There are 1111 ways in which five 6-sided dice (sides numbered 1 to 6) can be
    rolled so that the top three sum to 15. Some examples are:
    D1,D2,D3,D4,D5 = 4,3,6,3,5
    D1,D2,D3,D4,D5 = 4,3,3,5,6
    D1,D2,D3,D4,D5 = 3,3,3,6,6
    D1,D2,D3,D4,D5 = 6,6,3,3,3

    In how many ways can twenty 12-sided dice (sides numbered 1 to 12) be rolled
    so that the top ten sum to 70?

URL: https://projecteuler.net/problem=240
"""
from typing import Any

euler_problem: int = 240
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'G2ZWFQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
