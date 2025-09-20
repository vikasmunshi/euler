#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 657: Incomplete Words.

Problem Statement:
    In the context of formal languages, any finite sequence of letters of a given
    alphabet Σ is called a word over Σ. We call a word incomplete if it does not
    contain every letter of Σ.

    For example, using the alphabet Σ = {a, b, c}, 'ab', 'abab' and '' (the empty word)
    are incomplete words over Σ, while 'abac' is a complete word over Σ.

    Given an alphabet Σ of α letters, we define I(α,n) to be the number of incomplete
    words over Σ with a length not exceeding n.
    For example, I(3,0) = 1, I(3,2) = 13 and I(3,4) = 79.

    Find I(10^7, 10^12). Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=657
"""
from typing import Any

euler_problem: int = 657
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'alpha': 3, 'max_length': 2}, 'answer': None},
    {'category': 'main', 'input': {'alpha': 10000000, 'max_length': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
