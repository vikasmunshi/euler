#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 113: Non-bouncy Numbers.

Problem Statement:
    Working from left-to-right if no digit is exceeded by the digit to its left
    it is called an increasing number; for example, 134468.
    Similarly if no digit is exceeded by the digit to its right it is called a
    decreasing number; for example, 66420.
    We shall call a positive integer that is neither increasing nor decreasing a
    "bouncy" number; for example, 155349.
    As n increases, the proportion of bouncy numbers below n increases such that
    there are only 12951 numbers below one-million that are not bouncy and only
    277032 non-bouncy numbers below 10^10.
    How many numbers below a googol (10^100) are not bouncy?

URL: https://projecteuler.net/problem=113
"""
from typing import Any

euler_problem: int = 113
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_max_digits': 6}, 'answer': None},
    {'category': 'dev', 'input': {'num_max_digits': 10}, 'answer': None},
    {'category': 'main', 'input': {'num_max_digits': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
