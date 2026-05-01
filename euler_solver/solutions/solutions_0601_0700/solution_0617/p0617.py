#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 617: Mirror Power Sequence.

Problem Statement:
    For two integers n,e > 1, we define an (n,e)-MPS (Mirror Power Sequence) to be
    an infinite sequence of integers (a_i)_{i≥0} such that for all i≥0,
    a_{i+1} = min(a_i^e, n - a_i^e) and a_i > 1.

    Examples of such sequences are the two (18,2)-MPS sequences made of alternating
    2 and 4.

    Note that even though such a sequence is uniquely determined by n,e and a_0,
    for most values such a sequence does not exist. For example, no (n,e)-MPS exists
    for n < 6.

    Define C(n) to be the number of (n,e)-MPS for some e, and
    D(N) = sum_{n=2}^N C(n).

    You are given that D(10) = 2, D(100) = 21, D(1000) = 69, D(10^6) = 1303, and
    D(10^{12}) = 1014800.

    Find D(10^{18}).

URL: https://projecteuler.net/problem=617
"""
from typing import Any

euler_problem: int = 617
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'VGxGYb9dDbckrtxNXjHj8QsImkETwOFTGVqoqA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
