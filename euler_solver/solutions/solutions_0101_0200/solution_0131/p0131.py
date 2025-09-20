#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 131: Prime Cube Partnership.

Problem Statement:
    There are some prime values, p, for which there exists a positive integer, n,
    such that the expression n^3 + n^2 p is a perfect cube.

    For example, when p = 19, 8^3 + 8^2 * 19 = 12^3.

    What is perhaps most surprising is that for each prime with this property the
    value of n is unique, and there are only four such primes below one-hundred.

    How many primes below one million have this remarkable property?

URL: https://projecteuler.net/problem=131
"""
from typing import Any

euler_problem: int = 131
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
