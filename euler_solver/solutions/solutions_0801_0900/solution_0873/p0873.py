#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 873: Words with Gaps.

Problem Statement:
    Let W(p,q,r) be the number of words that can be formed using the letter A p times,
    the letter B q times and the letter C r times with the condition that every A is
    separated from every B by at least two Cs. For example, CACACCBB is a valid word for
    W(2,2,4) but ACBCACBC is not.

    You are given W(2,2,4)=32 and W(4,4,44)=13908607644.

    Find W(10^6,10^7,10^8). Give your answer modulo 1 000 000 007.

URL: https://projecteuler.net/problem=873
"""
from typing import Any

euler_problem: int = 873
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'p': 2, 'q': 2, 'r': 4}, 'answer': None},
    {'category': 'main', 'input': {'p': 1000000, 'q': 10000000, 'r': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
