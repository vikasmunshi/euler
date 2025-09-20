#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 539: Odd Elimination.

Problem Statement:
    Start from an ordered list of all integers from 1 to n. Going from left to right,
    remove the first number and every other number afterward until the end of the list.
    Repeat the procedure from right to left, removing the right most number and every other
    number from the numbers left. Continue removing every other numbers, alternating left
    to right and right to left, until a single number remains.

    Starting with n = 9, we have:
    1 2 3 4 5 6 7 8 9  (underlined numbers removed)
    2 4 6 8            (underlined numbers removed)
    2 6
    6

    Let P(n) be the last number left starting with a list of length n.
    Let S(n) = sum from k=1 to n of P(k).
    You are given P(1)=1, P(9)=6, P(1000)=510, and S(1000)=268271.

    Find S(10^18) modulo 987654321.

URL: https://projecteuler.net/problem=539
"""
from typing import Any

euler_problem: int = 539
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
