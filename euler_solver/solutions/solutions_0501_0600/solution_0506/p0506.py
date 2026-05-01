#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 506: Clock Sequence.

Problem Statement:
    Consider the infinite repeating sequence of digits:
    1234321234321234321...

    Amazingly, you can break this sequence of digits into a sequence of integers
    such that the sum of the digits in the n-th value is n.

    The sequence goes as follows:
    1, 2, 3, 4, 32, 123, 43, 2123, 432, 1234, 32123, ...

    Let v_n be the n-th value in this sequence. For example, v_2=2, v_5=32 and
    v_11=32123.

    Let S(n) be v_1+v_2+...+v_n. For example, S(11)=36120, and S(1000) mod 123454321=18232686.

    Find S(10^14) mod 123454321.

URL: https://projecteuler.net/problem=506
"""
from typing import Any

euler_problem: int = 506
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 11}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
    'gDXFMZrZDsw='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
