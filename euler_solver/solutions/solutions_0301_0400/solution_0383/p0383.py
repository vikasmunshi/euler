#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 383: Divisibility Comparison Between Factorials.

Problem Statement:
    Let f_5(n) be the largest integer x for which 5^x divides n.
    For example, f_5(625000) = 7.

    Let T_5(n) be the number of integers i which satisfy
    f_5((2 * i - 1)!) < 2 * f_5(i!) and 1 <= i <= n.
    It can be verified that T_5(10^3) = 68 and T_5(10^9) = 2408210.

    Find T_5(10^18).

URL: https://projecteuler.net/problem=383
"""
from typing import Any

euler_problem: int = 383
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'PnSbpCkr0knvBd2l'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
