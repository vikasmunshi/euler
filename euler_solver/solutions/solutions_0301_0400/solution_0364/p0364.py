#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 364: Comfortable Distance.

Problem Statement:
    There are N seats in a row. N people come after each other to fill the seats
    according to the following rules:

    1. If there is any seat whose adjacent seat(s) are not occupied take such a
       seat.
    2. If there is no such seat and there is any seat for which only one adjacent
       seat is occupied take such a seat.
    3. Otherwise take one of the remaining available seats.

    Let T(N) be the number of possibilities that N seats are occupied by N people
    with the given rules. The following figure shows T(4) = 8.

    We can verify that T(10) = 61632 and T(1,000) mod 100,000,007 = 47255094.

    Find T(1,000,000) mod 100,000,007.

URL: https://projecteuler.net/problem=364
"""
from typing import Any

euler_problem: int = 364
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 4}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Hd3Z3L8gx5Y='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
