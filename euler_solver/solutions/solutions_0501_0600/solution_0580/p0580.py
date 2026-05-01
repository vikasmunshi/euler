#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 580: Squarefree Hilbert Numbers.

Problem Statement:
    A Hilbert number is any positive integer of the form 4k+1 for integer k ≥ 0.
    We shall define a squarefree Hilbert number as a Hilbert number which is not
    divisible by the square of any Hilbert number other than one.
    For example, 117 is a squarefree Hilbert number, equaling 9×13.
    However 6237 is a Hilbert number that is not squarefree in this sense,
    as it is divisible by 9^2.
    The number 3969 is also not squarefree, as it is divisible by both 9^2 and 21^2.

    There are 2327192 squarefree Hilbert numbers below 10^7.
    How many squarefree Hilbert numbers are there below 10^16?

URL: https://projecteuler.net/problem=580
"""
from typing import Any

euler_problem: int = 580
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
