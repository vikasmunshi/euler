#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 929: Odd-Run Compositions.

Problem Statement:
    A composition of n is a sequence of positive integers which sum to n. Such a
    sequence can be split into runs, where a run is a maximal contiguous
    subsequence of equal terms.

    For example, 2,2,1,1,1,3,2,2 is a composition of 14 consisting of four runs:
    2, 2   1, 1, 1   3   2, 2

    Let F(n) be the number of compositions of n where every run has odd length.

    For example, F(5)=10:
        5     4,1     3,2     2,3     2,1,2
        2,1,1,1     1,4     1,3,1     1,1,1,2     1,1,1,1,1

    Find F(10^5). Give your answer modulo 1111124111.

URL: https://projecteuler.net/problem=929
"""
from typing import Any

euler_problem: int = 929
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
