#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 411: Uphill Paths.

Problem Statement:
    Let n be a positive integer. Suppose there are stations at the coordinates
    (x, y) = (2^i mod n, 3^i mod n) for 0 <= i <= 2n. We consider stations with
    the same coordinates as the same station.

    We wish to form a path from (0, 0) to (n, n) such that the x and y coordinates
    never decrease.
    Let S(n) be the maximum number of stations such a path can pass through.

    For example, if n = 22, there are 11 distinct stations, and a valid path can
    pass through at most 5 stations. Therefore, S(22) = 5.
    The case is illustrated with an example of an optimal path.

    It can also be verified that S(123) = 14 and S(10000) = 48.

    Find the sum of S(k^5) for 1 <= k <= 30.

URL: https://projecteuler.net/problem=411
"""
from typing import Any

euler_problem: int = 411
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 22}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 6436343}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
