#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 427: n-sequences.

Problem Statement:
    A sequence of integers S = {s_i} is called an n-sequence if it has n elements
    and each element s_i satisfies 1 ≤ s_i ≤ n. Thus there are n^n distinct n-sequences
    in total.
    For example, the sequence S = {1, 5, 5, 10, 7, 7, 7, 2, 3, 7} is a 10-sequence.

    For any sequence S, let L(S) be the length of the longest contiguous subsequence
    of S with the same value.
    For example, for the given sequence S above, L(S) = 3, because of the three
    consecutive 7's.

    Let f(n) = sum of L(S) for all n-sequences S.

    For example, f(3) = 45, f(7) = 1403689 and f(11) = 481496895121.

    Find f(7,500,000) mod 1,000,000,009.

URL: https://projecteuler.net/problem=427
"""
from typing import Any

euler_problem: int = 427
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 7500000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'HqBFGumnnUA='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
