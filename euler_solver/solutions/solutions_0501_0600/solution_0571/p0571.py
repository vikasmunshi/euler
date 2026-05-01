#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 571: Super Pandigital Numbers.

Problem Statement:
    A positive number is pandigital in base b if it contains all digits from 0 to b - 1
    at least once when written in base b.

    An n-super-pandigital number is a number that is simultaneously pandigital in all bases
    from 2 to n inclusively.
    For example 978 = 1111010010_2 = 1100020_3 = 33102_4 = 12403_5 is the smallest 5-super-
    pandigital number.
    Similarly, 1093265784 is the smallest 10-super-pandigital number.
    The sum of the 10 smallest 10-super-pandigital numbers is 20319792309.

    What is the sum of the 10 smallest 12-super-pandigital numbers?

URL: https://projecteuler.net/problem=571
"""
from typing import Any

euler_problem: int = 571
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 12}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
