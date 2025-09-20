#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 490: Jumping Frog.

Problem Statement:
    There are n stones in a pond, numbered 1 to n. Consecutive stones are spaced one unit apart.

    A frog sits on stone 1. He wishes to visit each stone exactly once, stopping on stone n.
    However, he can only jump from one stone to another if they are at most 3 units apart.
    In other words, from stone i, he can reach a stone j if 1 <= j <= n and j is in the set
    {i-3, i-2, i-1, i+1, i+2, i+3}.

    Let f(n) be the number of ways he can do this. For example, f(6) = 14, as shown below:
    1 -> 2 -> 3 -> 4 -> 5 -> 6
    1 -> 2 -> 3 -> 5 -> 4 -> 6
    1 -> 2 -> 4 -> 3 -> 5 -> 6
    1 -> 2 -> 4 -> 5 -> 3 -> 6
    1 -> 2 -> 5 -> 3 -> 4 -> 6
    1 -> 2 -> 5 -> 4 -> 3 -> 6
    1 -> 3 -> 2 -> 4 -> 5 -> 6
    1 -> 3 -> 2 -> 5 -> 4 -> 6
    1 -> 3 -> 4 -> 2 -> 5 -> 6
    1 -> 3 -> 5 -> 2 -> 4 -> 6
    1 -> 4 -> 2 -> 3 -> 5 -> 6
    1 -> 4 -> 2 -> 5 -> 3 -> 6
    1 -> 4 -> 3 -> 2 -> 5 -> 6
    1 -> 4 -> 5 -> 2 -> 3 -> 6

    Other examples are f(10) = 254 and f(40) = 1439682432976.

    Let S(L) = sum f(n)^3 for 1 <= n <= L.
    Examples:
    S(10) = 18230635
    S(20) = 104207881192114219
    S(1,000) mod 10^9 = 225031475
    S(1,000,000) mod 10^9 = 363486179

    Find S(10^14) mod 10^9.

URL: https://projecteuler.net/problem=490
"""
from typing import Any

euler_problem: int = 490
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
