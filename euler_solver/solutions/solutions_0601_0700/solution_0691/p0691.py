#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 691: Long Substring with Many Repetitions.

Problem Statement:
    Given a character string s, we define L(k,s) to be the length of the longest
    substring of s which appears at least k times in s, or 0 if such a substring
    does not exist. For example, L(3,"bbabcabcabcacba")=4 because of the three
    occurrences of the substring "abca", and L(2,"bbabcabcabcacba")=7 because
    of the repeated substring "abcabca". Note that the occurrences can overlap.

    Let a_n, b_n and c_n be the 0/1 sequences defined by:
        a_0 = 0
        a_{2n} = a_{n}
        a_{2n+1} = 1-a_{n}
        b_n = floor((n+1)/φ) - floor(n/φ) (where φ is the golden ratio)
        c_n = a_n + b_n - 2 a_n b_n
    and S_n the character string c_0 ... c_{n-1}. You are given that
    L(2,S_10)=5, L(3,S_10)=2, L(2,S_100)=14, L(4,S_100)=6, L(2,S_1000)=86,
    L(3,S_1000)=45, L(5,S_1000)=31, and that the sum of non-zero L(k,S_1000) for k≥1
    is 2460.

    Find the sum of non-zero L(k,S_5000000) for k≥1.

URL: https://projecteuler.net/problem=691
"""
from typing import Any

euler_problem: int = 691
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 5000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
