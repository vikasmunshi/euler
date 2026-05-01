#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 461: Almost Pi.

Problem Statement:
    Let f_n(k) = e^(k/n) - 1, for all non-negative integers k.

    Remarkably, f_200(6) + f_200(75) + f_200(89) + f_200(226) = 3.1415926...
    approximately pi.

    In fact, it is the best approximation of pi of the form
    f_n(a) + f_n(b) + f_n(c) + f_n(d) for n = 200.

    Let g(n) = a^2 + b^2 + c^2 + d^2 for a, b, c, d that minimize the error:
    |f_n(a) + f_n(b) + f_n(c) + f_n(d) - pi|
    (where |x| denotes the absolute value of x).

    You are given g(200) = 6^2 + 75^2 + 89^2 + 226^2 = 64658.

    Find g(10000).

URL: https://projecteuler.net/problem=461
"""
from typing import Any

euler_problem: int = 461
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 200}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
