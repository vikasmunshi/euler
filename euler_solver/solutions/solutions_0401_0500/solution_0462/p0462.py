#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 462: Permutation of 3-smooth Numbers.

Problem Statement:
    A 3-smooth number is an integer which has no prime factor larger than 3. For an
    integer N, we define S(N) as the set of 3-smooth numbers less than or equal to N.
    For example, S(20) = { 1, 2, 3, 4, 6, 8, 9, 12, 16, 18 }.

    We define F(N) as the number of permutations of S(N) in which each element comes
    after all of its proper divisors.

    This is one of the possible permutations for N = 20.
    - 1, 2, 4, 3, 9, 8, 16, 6, 18, 12.
    This is not a valid permutation because 12 comes before its divisor 6.
    - 1, 2, 4, 3, 9, 8, 12, 16, 6, 18.

    We can verify that F(6) = 5, F(8) = 9, F(20) = 450 and F(1000) ≈ 8.8521816557e21.
    Find F(10^18). Give as your answer its scientific notation rounded to ten digits
    after the decimal point.
    When giving your answer, use a lowercase e to separate mantissa and exponent.
    E.g. if the answer is 112233445566778899 then the answer format would be
    1.1223344557e17.

URL: https://projecteuler.net/problem=462
"""
from typing import Any

euler_problem: int = 462
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Wt25apa77ctchWwz'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
