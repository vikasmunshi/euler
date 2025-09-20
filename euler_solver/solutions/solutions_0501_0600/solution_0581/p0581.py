#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 581: 47-smooth Triangular Numbers.

Problem Statement:
    A number is p-smooth if it has no prime factors larger than p.
    Let T be the sequence of triangular numbers, i.e. T(n) = n(n+1)/2.
    Find the sum of all indices n such that T(n) is 47-smooth.

URL: https://projecteuler.net/problem=581
"""
from typing import Any

euler_problem: int = 581
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'oMgTSy+3ysbICFO0ZDUFbOqoWM0='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
