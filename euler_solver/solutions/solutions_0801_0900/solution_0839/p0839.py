#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 839: Beans in Bowls.

Problem Statement:
    The sequence S_n is defined by S_0 = 290797 and S_n = S_{n-1}^2 mod 50515093
    for n > 0.

    There are N bowls indexed 0,1,...,N-1. Initially there are S_n beans in bowl n.

    At each step, the smallest index n is found such that bowl n has strictly more
    beans than bowl n+1. Then one bean is moved from bowl n to bowl n+1.

    Let B(N) be the number of steps needed to sort the bowls into non-descending
    order.
    For example, B(5) = 0, B(6) = 14263289 and B(100) = 3284417556.

    Find B(10^7).

URL: https://projecteuler.net/problem=839
"""
from typing import Any

euler_problem: int = 839
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 6}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
