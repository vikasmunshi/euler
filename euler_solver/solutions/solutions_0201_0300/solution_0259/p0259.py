#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 259: Reachable Numbers.

Problem Statement:
    A positive integer will be called reachable if it can result from an
    arithmetic expression obeying the following rules:
    - Uses the digits 1 through 9, in that order and exactly once each.
    - Any successive digits can be concatenated (for example, using the digits
      2, 3 and 4 we obtain the number 234).
    - Only the four usual binary arithmetic operations (addition, subtraction,
      multiplication and division) are allowed.
    - Each operation can be used any number of times, or not at all.
    - Unary minus is not allowed.
    - Any number of (possibly nested) parentheses may be used to define the
      order of operations.
    For example, 42 is reachable, since (1 / 23) * ((4 * 5) - 6) * (78 - 9) = 42.
    What is the sum of all positive reachable integers?

URL: https://projecteuler.net/problem=259
"""
from typing import Any

euler_problem: int = 259
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
