#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 118: Pandigital Prime Sets.

Problem Statement:
    Using all of the digits 1 through 9 and concatenating them freely to form
    decimal integers, different sets can be formed. Interestingly with the set
    {2,5,47,89,631}, all of the elements belonging to it are prime.

    How many distinct sets containing each of the digits one through nine exactly
    once contain only prime elements?

URL: https://projecteuler.net/problem=118
"""
from typing import Any

euler_problem: int = 118
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'lxNJAkqY6auY8Ms4P5vXfg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
