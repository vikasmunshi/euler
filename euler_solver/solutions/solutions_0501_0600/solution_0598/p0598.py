#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 598: Split Divisibilities.

Problem Statement:
    Consider the number 48.
    There are five pairs of integers a and b (a <= b) such that a * b = 48:
    (1,48), (2,24), (3,16), (4,12) and (6,8).
    It can be seen that both 6 and 8 have 4 divisors.
    So of those five pairs one consists of two integers with the same number of divisors.

    In general:
    Let C(n) be the number of pairs of positive integers a times b equals n,
    (a <= b) such that a and b have the same number of divisors;
    so C(48) = 1.

    You are given C(10!) = 3: (1680, 2160), (1800, 2016) and (1890, 1920).

    Find C(100!).

URL: https://projecteuler.net/problem=598
"""
from typing import Any

euler_problem: int = 598
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 100}, 'answer': None},
]
encrypted: str = (
    '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'
    'MwSIwhjg7IRsVBW4M0x+4BBkYZXK3HIkG5J2Rg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
