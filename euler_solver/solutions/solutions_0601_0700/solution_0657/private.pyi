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

Solution Approach:
    Use combinatorics and inclusion–exclusion principle to count incomplete words.
    Key idea is to count all words up to length n and subtract those containing all letters.
    Employ fast modular arithmetic and exponentiation for large inputs.
    Expected O(α log n) or better using efficient power and combination computations.

Answer: ...
URL: https://projecteuler.net/problem=657
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 657
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'alpha': 3, 'max_length': 2}},
    {'category': 'main', 'input': {'alpha': 10000000, 'max_length': 1000000000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_incomplete_words_p0657_s0(*, alpha: int, max_length: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))