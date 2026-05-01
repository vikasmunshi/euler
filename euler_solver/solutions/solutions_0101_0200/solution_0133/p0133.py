#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 133: Repunit Nonfactors.

Problem Statement:
    A number consisting entirely of ones is called a repunit. We shall define
    R(k) to be a repunit of length k; for example, R(6) = 111111.

    Let us consider repunits of the form R(10^n).

    Although R(10), R(100), or R(1000) are not divisible by 17, R(10000) is
    divisible by 17. Yet there is no value of n for which R(10^n) will divide
    by 19. In fact, it is remarkable that 11, 17, 41, and 73 are the only four
    primes below one-hundred that can be a factor of R(10^n).

    Find the sum of all the primes below one-hundred thousand that will never
    be a factor of R(10^n).

URL: https://projecteuler.net/problem=133
"""
from typing import Any

euler_problem: int = 133
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 200000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
