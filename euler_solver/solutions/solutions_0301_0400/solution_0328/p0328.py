#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 328: Lowest-cost Search.

Problem Statement:
    We are trying to find a hidden number selected from the set of integers
    {1, 2, ..., n} by asking questions. Each question is a guess (a number)
    and has a cost equal to the number asked. Each answer is one of:
        "Your guess is lower than the hidden number",
        "Yes, that's it!",
        "Your guess is higher than the hidden number".
    An optimal strategy minimizes the total cost (the sum of all asked
    numbers) for the worst possible case.

    Examples:
        For n = 3, ask "2" and the hidden number is found immediately; cost = 2.
        For n = 8, a binary-search style strategy (4, 6, 7) yields worst-case
        cost 4 + 6 + 7 = 17. A better first guess is 5; then worst-case cost is
        12 (e.g. 5 + 7) and the strategy described achieves C(8) = 12.

    Let C(n) be the worst-case cost achieved by an optimal strategy. Given:
        C(1) = 0, C(2) = 1, C(3) = 2, C(8) = 12,
        C(100) = 400 and sum_{n=1..100} C(n) = 17575.
    Find sum_{n=1..200000} C(n).

URL: https://projecteuler.net/problem=328
"""
from typing import Any

euler_problem: int = 328
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 200000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
