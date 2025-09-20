#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 238: Infinite String Tour.

Problem Statement:
    Create a sequence of numbers using the "Blum Blum Shub" pseudo-random
    number generator:
    s_0 = 14025256
    s_{n + 1} = s_n^2 mod 20300713

    Concatenate these numbers s_0 s_1 s_2 ... to create a string w of
    infinite length.
    Then, w = 14025256741014958470038053646...

    For a positive integer k, if no substring of w exists with a sum of
    digits equal to k, p(k) is defined to be zero. If at least one
    substring of w exists with a sum of digits equal to k, we define
    p(k) = z, where z is the starting position of the earliest such
    substring.

    For instance:
    The substrings 1, 14, 1402, ... with respective sums of digits equal
    to 1, 5, 7, ... start at position 1, hence p(1) = p(5) = p(7) = ... = 1.
    The substrings 4, 402, 4025, ... with respective sums equal to 4, 6,
    11, ... start at position 2, hence p(4) = p(6) = p(11) = ... = 2.
    The substrings 02, 0252, ... with respective sums equal to 2, 9, ...
    start at position 3, hence p(2) = p(9) = ... = 3.
    Note that substring 025 starting at position 3 has sum 7, but there was
    an earlier substring (starting at position 1) with sum 7, so p(7) = 1.

    We can verify that, for 0 < k <= 10^3, sum p(k) = 4742.

    Find sum p(k) for 0 < k <= 2*10^15.

URL: https://projecteuler.net/problem=238
"""
from typing import Any

euler_problem: int = 238
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 2000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 20000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'w2AHUw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
