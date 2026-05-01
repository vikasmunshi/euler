#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 164: Three Consecutive Digital Sum Limit.

Problem Statement:
    How many 20 digit numbers n (without any leading zero) exist such that no
    three consecutive digits of n have a sum greater than 9?

URL: https://projecteuler.net/problem=164
"""
from typing import Any

euler_problem: int = 164
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_digits': 3}, 'answer': None},
    {'category': 'main', 'input': {'num_digits': 20}, 'answer': None},
    {'category': 'extra', 'input': {'num_digits': 25}, 'answer': None},
]
encrypted: str = (
    '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'
    'UDS/FYeirhMPnCV6rFVoJ/wW/1Y='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
