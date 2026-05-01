#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 181: Grouping Two Different Coloured Objects.

Problem Statement:
    Having three black objects B and one white object W they can be grouped in
    7 ways like this:
    (BBBW) (B,BBW) (B,B,BW) (B,B,B,W) (B,BB,W) (BBB,W) (BB,BW)

    In how many ways can sixty black objects B and forty white objects W be
    thus grouped?

URL: https://projecteuler.net/problem=181
"""
from typing import Any

euler_problem: int = 181
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'black': 3, 'white': 1}, 'answer': None},
    {'category': 'main', 'input': {'black': 60, 'white': 40}, 'answer': None},
    {'category': 'extra', 'input': {'black': 100, 'white': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
