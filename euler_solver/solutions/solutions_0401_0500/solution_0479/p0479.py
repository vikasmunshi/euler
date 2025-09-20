#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 479: Roots on the Rise.

Problem Statement:
    Let a_k, b_k, and c_k represent the three solutions (real or complex numbers)
    to the equation 1/x = (k/x)^2 * (k + x^2) - k * x.

    For instance, for k=5, the set {a_5, b_5, c_5} is approximately
    {5.727244, -0.363622+2.057397i, -0.363622-2.057397i}.

    Define S(n) = sum from p=1 to n of sum from k=1 to n of
    (a_k + b_k)^p * (b_k + c_k)^p * (c_k + a_k)^p.

    Interestingly, S(n) is always an integer. For example, S(4) = 51160.

    Find S(10^6) modulo 1,000,000,007.

URL: https://projecteuler.net/problem=479
"""
from typing import Any

euler_problem: int = 479
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
