#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 803: Pseudorandom Sequence.

Problem Statement:
    Rand48 is a pseudorandom number generator used by some programming languages.
    It generates a sequence from any given integer 0 <= a_0 < 2^48 using the rule
    a_n = (25214903917 * a_{n-1} + 11) mod 2^48.

    Let b_n = floor(a_n / 2^16) mod 52.
    The sequence b_0, b_1, ... is translated to an infinite string c = c_0 c_1 ... via:
    0 -> a, 1 -> b, ..., 25 -> z, 26 -> A, 27 -> B, ..., 51 -> Z.

    For example, if a_0 = 123456, then c starts with "bQYicNGCY...".
    Starting from index 100, the substring "RxqLBfWzv" occurs for the first time.

    Alternatively, if c starts with "EULERcats...", then a_0 = 78580612777175.

    Now suppose c starts with "PuzzleOne...".
    Find the starting index of the first occurrence of substring "LuckyText" in c.

URL: https://projecteuler.net/problem=803
"""
from typing import Any

euler_problem: int = 803
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
