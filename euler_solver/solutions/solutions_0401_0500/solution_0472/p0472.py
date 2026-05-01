#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 472: Comfortable Distance II.

Problem Statement:
    There are N seats in a row. N people come one after another to fill the seats
    according to the following rules:
        1. No person sits beside another.
        2. The first person chooses any seat.
        3. Each subsequent person chooses the seat furthest from anyone else already
           seated, as long as it does not violate rule 1. If there is more than one
           choice satisfying this condition, then the person chooses the leftmost choice.

    Note that due to rule 1, some seats will surely be left unoccupied, and the
    maximum number of people that can be seated is less than N (for N > 1).

    For example, for N = 15, when the first person chooses correctly, the 15 seats
    can seat up to 7 people. The first person has 9 choices to maximize the number
    of occupants.

    Let f(N) be the number of choices the first person has to maximize the number
    of occupants for N seats in a row. Thus, f(1) = 1, f(15) = 9, f(20) = 6,
    and f(500) = 16. Also, sum f(N) = 83 for 1 <= N <= 20 and sum f(N) = 13343 for
    1 <= N <= 500.

    Find sum f(N) for 1 <= N <= 10^12. Give the last 8 digits of your answer.

URL: https://projecteuler.net/problem=472
"""
from typing import Any

euler_problem: int = 472
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 20}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
