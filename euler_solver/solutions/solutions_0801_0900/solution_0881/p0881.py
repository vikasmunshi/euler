#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 881: Divisor Graph Width.

Problem Statement:
    For a positive integer n create a graph using its divisors as vertices.
    An edge is drawn between two vertices a < b if their quotient b/a is
    prime. The graph can be arranged into levels where vertex n is at level 0
    and vertices that are a distance k from n are on level k. Define g(n) to
    be the maximum number of vertices in a single level.

    The example above shows that g(45) = 2. You are also given g(5040) = 12.

    Find the smallest number n such that g(n) >= 10000.

URL: https://projecteuler.net/problem=881
"""
from typing import Any

euler_problem: int = 881
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
