#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 330: Euler's Number.

Problem Statement:
    An infinite sequence of real numbers a(n) is defined for all integers n as
    follows:
    a(n) = 1 for n < 0
    a(n) = sum_{i=1}^infty a(n - i)/i! for n >= 0

    For example,
    a(0) = 1/1! + 1/2! + 1/3! + ... = e - 1
    a(1) = (e - 1)/1! + 1/2! + 1/3! + ... = 2e - 3
    a(2) = (2e - 3)/1! + (e - 1)/2! + 1/3! + ... = (7/2)e - 6

    with e = 2.7182818... being Euler's constant.

    It can be shown that a(n) is of the form (A(n)e + B(n))/n! for integers
    A(n) and B(n).

    For example, a(10) = (328161643e - 652694486)/10!.

    Find A(10^9) + B(10^9) and give your answer mod 77777777.

URL: https://projecteuler.net/problem=330
"""
from typing import Any

euler_problem: int = 330
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'IIiiJUEZmacHjutfzM9sMPBXBRwZcN9RYaHPZw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
