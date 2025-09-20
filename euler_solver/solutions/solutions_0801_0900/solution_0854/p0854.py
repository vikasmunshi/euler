#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 854: Pisano Periods 2.

Problem Statement:
    For every positive integer n the Fibonacci sequence modulo n is periodic. The period
    depends on the value of n. This period is called the Pisano period for n, often
    shortened to π(n).

    Define M(p) as the largest integer n such that π(n) = p, and define M(p) = 1 if there is
    no such n. For example, there are three values of n for which π(n) equals 18: 19, 38,
    76. Therefore M(18) = 76.

    Let the product function P(n) be:
        P(n) = ∏_{p=1}^{n} M(p).

    You are given: P(10) = 264.

    Find P(1,000,000) modulo 1,234,567,891.

URL: https://projecteuler.net/problem=854
"""
from typing import Any

euler_problem: int = 854
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_p': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_p': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '8cMnW9L6I0JDPSo5uRj/SR34r63DXo/N'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
