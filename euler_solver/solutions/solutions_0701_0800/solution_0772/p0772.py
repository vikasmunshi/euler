#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 772: Balanceable k-bounded Partitions.

Problem Statement:
    A k-bounded partition of a positive integer N is a way of writing N as a sum of
    positive integers not exceeding k.

    A balanceable partition is a partition that can be further divided into two parts
    of equal sums.

    For example, 3 + 2 + 2 + 2 + 2 + 1 is a balanceable 3-bounded partition of 12
    since 3 + 2 + 1 = 2 + 2 + 2. Conversely, 3 + 3 + 3 + 1 is a 3-bounded partition
    of 10 which is not balanceable.

    Let f(k) be the smallest positive integer N all of whose k-bounded partitions are
    balanceable. For example, f(3) = 12 and f(30) ≡ 179092994 mod 1000000007.

    Find f(10^8). Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=772
"""
from typing import Any

euler_problem: int = 772
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'k': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
