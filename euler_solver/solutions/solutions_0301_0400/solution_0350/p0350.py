#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 350: Constraining the Least Greatest and the Greatest Least.

Problem Statement:
    A list of size n is a sequence of n natural numbers. Examples are (2,4,6),
    (2,6,4), (10,6,15,6) and (11).

    The greatest common divisor, or gcd, of a list is the largest natural
    number that divides all entries of the list. Examples: gcd(2,6,4) = 2,
    gcd(10,6,15,6) = 1 and gcd(11) = 11.

    The least common multiple, or lcm, of a list is the smallest natural
    number divisible by each entry of the list. Examples: lcm(2,6,4) = 12,
    lcm(10,6,15,6) = 30 and lcm(11) = 11.

    Let f(G, L, N) be the number of lists of size N with gcd >= G and lcm
    <= L. For example:
    f(10, 100, 1) = 91.
    f(10, 100, 2) = 327.
    f(10, 100, 3) = 1135.
    f(10, 100, 1000) mod 101^4 = 3286053.

    Find f(10^6, 10^12, 10^18) mod 101^4.

URL: https://projecteuler.net/problem=350
"""
from typing import Any

euler_problem: int = 350
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'G': 10, 'L': 100, 'N': 1}, 'answer': None},
    {'category': 'main', 'input': {'G': 1000000, 'L': 1000000000000, 'N': 1000000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'G': 1000, 'L': 1000000, 'N': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Wml6RfzGWdEKFcWn'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
