#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 162: Hexadecimal Numbers.

Problem Statement:
    In the hexadecimal number system numbers are represented using 16 different
    digits: 0,1,2,3,4,5,6,7,8,9,A,B,C,D,E,F.

    The hexadecimal number AF when written in the decimal number system equals
    10 * 16 + 15 = 175.

    In the 3-digit hexadecimal numbers 10A, 1A0, A10, and A01 the digits 0, 1
    and A are all present. Like numbers written in base ten we write
    hexadecimal numbers without leading zeroes.

    How many hexadecimal numbers containing at most sixteen hexadecimal digits
    exist with all of the digits 0, 1, and A present at least once?
    Give your answer as a hexadecimal number.

    (A, B, C, D, E and F in upper case, without any leading or trailing code
    that marks the number as hexadecimal and without leading zeroes, e.g. 1A3F
    and not: 1a3f and not 0x1a3f and not 1A3F and not #1A3F and not
    0000001A3F)

URL: https://projecteuler.net/problem=162
"""
from typing import Any

euler_problem: int = 162
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_digits': 3}, 'answer': None},
    {'category': 'main', 'input': {'max_digits': 16}, 'answer': None},
    {'category': 'extra', 'input': {'max_digits': 20}, 'answer': None},
]
encrypted: str = (
    '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'
    '+p0hOxog6OH1qTbfvxRRag=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
