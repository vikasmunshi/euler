#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 112: Bouncy Numbers.

Problem Statement:
    Working from left-to-right, if no digit is exceeded by the digit to its
    left it is called an increasing number; for example, 134468.

    Similarly, if no digit is exceeded by the digit to its right it is called a
    decreasing number; for example, 66420.

    A positive integer that is neither increasing nor decreasing is called a
    "bouncy" number; for example, 155349.

    There are no bouncy numbers below one-hundred, but just over half of the
    numbers below one-thousand (525) are bouncy. The least number for which the
    proportion of bouncy numbers first reaches 50% is 538.

    By the time we reach 21780 the proportion of bouncy numbers is 90%.

    Find the least number for which the proportion of bouncy numbers is
    exactly 99%.

URL: https://projecteuler.net/problem=112
"""
from typing import Any

euler_problem: int = 112
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'target_percentage': 50}, 'answer': None},
    {'category': 'dev', 'input': {'target_percentage': 90}, 'answer': None},
    {'category': 'main', 'input': {'target_percentage': 99}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
