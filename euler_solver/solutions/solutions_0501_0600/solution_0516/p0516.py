#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 516: 5-smooth Totients.

Problem Statement:
    5-smooth numbers are numbers whose largest prime factor doesn't exceed 5.
    5-smooth numbers are also called Hamming numbers.
    Let S(L) be the sum of the numbers n not exceeding L such that Euler's totient
    function φ(n) is a Hamming number.
    S(100)=3728.

    Find S(10^12). Give your answer modulo 2^32.

URL: https://projecteuler.net/problem=516
"""
from typing import Any

euler_problem: int = 516
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'HCxg8vRByOt9Al/My2CNyg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
