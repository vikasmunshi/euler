#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 588: Quintinomial Coefficients.

Problem Statement:
    The coefficients in the expansion of (x+1)^k are called binomial coefficients.
    Analogously the coefficients in the expansion of (x^4+x^3+x^2+x+1)^k are
    called quintinomial coefficients (quintus= Latin for fifth).

    Consider the expansion of (x^4+x^3+x^2+x+1)^3:
    x^12 + 3x^11 + 6x^10 + 10x^9 + 15x^8 + 18x^7 + 19x^6 + 18x^5 + 15x^4 +
    10x^3 + 6x^2 + 3x + 1
    As we can see 7 out of the 13 quintinomial coefficients for k=3 are odd.

    Let Q(k) be the number of odd coefficients in the expansion of
    (x^4+x^3+x^2+x+1)^k.
    So Q(3)=7.

    You are given Q(10)=17 and Q(100)=35.

    Find the sum of Q(10^k) for k=1 to 18.

URL: https://projecteuler.net/problem=588
"""
from typing import Any

euler_problem: int = 588
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_power': 3}, 'answer': None},
    {'category': 'main', 'input': {'max_power': 18}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
