#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 158: Lexicographical Neighbours.

Problem Statement:
    Taking three different letters from the 26 letters of the alphabet,
    character strings of length three can be formed. Examples are 'abc',
    'hat' and 'zyx'. When we study these three examples we see that for
    'abc' two characters come lexicographically after its neighbour to the
    left. For 'hat' there is exactly one character that comes lexicographically
    after its neighbour to the left. For 'zyx' there are zero characters that
    come lexicographically after its neighbour to the left. In all there are
    10400 strings of length 3 for which exactly one character comes
    lexicographically after its neighbour to the left.

    We now consider strings of n <= 26 different characters from the alphabet.
    For every n, p(n) is the number of strings of length n for which exactly
    one character comes lexicographically after its neighbour to the left.

    What is the maximum value of p(n)?

URL: https://projecteuler.net/problem=158
"""
from typing import Any

euler_problem: int = 158
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 3}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 26}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 20}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
