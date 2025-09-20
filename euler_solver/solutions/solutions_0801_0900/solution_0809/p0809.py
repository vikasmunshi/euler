#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 809: Rational Recurrence Relation.

Problem Statement:
    The following is a function defined for all positive rational values of x.

        f(x) =
            x                    if x is integral
            f(1/(1 - x))          if x < 1
            f(1/(ceil(x) - x) - 1 + f(x - 1)) otherwise

    For example, f(3/2) = 3, f(1/6) = 65533 and f(13/10) = 7625597484985.

    Find f(22/7). Give your answer modulo 10^15.

URL: https://projecteuler.net/problem=809
"""
from typing import Any

euler_problem: int = 809
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'aAJjhw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
