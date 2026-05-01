#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 658: Incomplete Words II.

Problem Statement:
    In the context of formal languages, any finite sequence of letters of a given
    alphabet Σ is called a word over Σ. We call a word incomplete if it does not
    contain every letter of Σ.

    For example, using the alphabet Σ = {a, b, c}, 'ab', 'abab' and '' (the empty
    word) are incomplete words over Σ, while 'abac' is a complete word over Σ.

    Given an alphabet Σ of α letters, we define I(α,n) to be the number of incomplete
    words over Σ with a length not exceeding n.
    For example, I(3,0) = 1, I(3,2) = 13 and I(3,4) = 79.

    Let S(k,n) = ∑_{α=1}^k I(α,n).
    For example, S(4,4) = 406, S(8,8) = 27902680 and S(10,100) ≡ 983602076 mod 1,000,000,007.

    Find S(10^7, 10^{12}). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=658
"""
from typing import Any

euler_problem: int = 658
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'k': 10000000, 'n': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
