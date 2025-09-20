#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 396: Weak Goodstein Sequence.

Problem Statement:
    For any positive integer n, the nth weak Goodstein sequence {g1, g2, g3, ...}
    is defined as:
    g1 = n
    for k > 1, gk is obtained by writing g{k-1} in base k, interpreting it as a
    base k+1 number, and subtracting 1.
    The sequence terminates when gk becomes 0.

    For example, the 6th weak Goodstein sequence is {6, 11, 17, 25, ...}:
    g1 = 6.
    g2 = 11 since 6 = 110_2, 110_3 = 12, and 12 - 1 = 11.
    g3 = 17 since 11 = 102_3, 102_4 = 18, and 18 - 1 = 17.
    g4 = 25 since 17 = 101_4, 101_5 = 26, and 26 - 1 = 25.

    It can be shown that every weak Goodstein sequence terminates.

    Let G(n) be the number of nonzero elements in the nth weak Goodstein
    sequence. It can be verified that G(2) = 3, G(4) = 21 and G(6) = 381.
    It can also be verified that sum G(n) = 2517 for 1 <= n < 8.

    Find the last 9 digits of sum G(n) for 1 <= n < 16.

URL: https://projecteuler.net/problem=396
"""
from typing import Any

euler_problem: int = 396
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 8}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 16}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 20}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
