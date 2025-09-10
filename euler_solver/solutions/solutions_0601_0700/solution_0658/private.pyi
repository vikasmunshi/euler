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

Solution Approach:
    Apply combinatorics and inclusion-exclusion principle to count incomplete words.
    Use modular arithmetic to handle large powers and sums.
    Key idea: compute total words and subtract complete words using inclusion-exclusion.
    Efficient exponentiation and summation formulas for large n and k are essential.
    Time complexity depends on fast exponentiation and summation optimizations modulo.

Answer: ...
URL: https://projecteuler.net/problem=658
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 658
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'k': 10_000_000, 'n': 10**12}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_incomplete_words_ii_p0658_s0(*, k: int, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))