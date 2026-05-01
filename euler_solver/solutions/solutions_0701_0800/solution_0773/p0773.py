#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 773: Ruff Numbers.

Problem Statement:
    Let S_k be the set containing 2 and 5 and the first k primes that end in 7.
    For example, S_3 = {2, 5, 7, 17, 37}.

    Define a k-Ruff number to be one that is not divisible by any element in S_k.

    If N_k is the product of the numbers in S_k then define F(k) to be the sum of all
    k-Ruff numbers less than N_k that have last digit 7. You are given F(3) = 76101452.

    Find F(97), give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=773
"""
from typing import Any

euler_problem: int = 773
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 3}, 'answer': None},
    {'category': 'main', 'input': {'k': 97}, 'answer': None},
]
encrypted: str = (
    '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'
    'RUW/DFKJTUACwp+N1fCdUiOHloc+5Fid'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
