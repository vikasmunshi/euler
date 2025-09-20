#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 302: Strong Achilles Numbers.

Problem Statement:
    A positive integer n is powerful if p^2 is a divisor of n for every prime
    factor p in n.

    A positive integer n is a perfect power if n can be expressed as a power of
    another positive integer.

    A positive integer n is an Achilles number if n is powerful but not a perfect
    power. For example, 864 and 1800 are Achilles numbers: 864 = 2^5 * 3^3 and
    1800 = 2^3 * 3^2 * 5^2.

    We shall call a positive integer S a Strong Achilles number if both S and
    phi(S) are Achilles numbers. For example, 864 is a Strong Achilles number:
    phi(864) = 288 = 2^5 * 3^2. However, 1800 isn't a Strong Achilles number
    because: phi(1800) = 480 = 2^5 * 3^1 * 5^1.

    There are 7 Strong Achilles numbers below 10^4 and 656 below 10^8.

    How many Strong Achilles numbers are there below 10^18?

    (phi denotes Euler's totient function.)

URL: https://projecteuler.net/problem=302
"""
from typing import Any

euler_problem: int = 302
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'kDqPee+PKUpuXnZg3QzIbDXTmacpbGlx'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
