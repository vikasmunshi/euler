#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 656: Palindromic Sequences.

Problem Statement:
    Given an irrational number alpha, let S_alpha(n) be the sequence
    S_alpha(n) = floor(alpha * n) - floor(alpha * (n-1)) for n >= 1.
    (floor denotes the floor-function.)

    It can be proven that for any irrational alpha there exist infinitely many
    values of n such that the subsequence {S_alpha(1), S_alpha(2), ..., S_alpha(n)}
    is palindromic.

    The first 20 values of n that yield a palindromic subsequence for alpha = sqrt(31)
    are: 1, 3, 5, 7, 44, 81, 118, 273, 3158, 9201, 15244, 21287, 133765,
    246243, 358721, 829920, 9600319, 27971037, 46341755, 64712473.

    Let H_g(alpha) be the sum of the first g values of n for which the corresponding
    subsequence is palindromic.
    For example, H_20(sqrt(31)) = 150243655.

    Let T = {2, 3, 5, 6, 7, 8, 10, ..., 1000} be the set of positive integers not exceeding
    1000 excluding perfect squares.
    Calculate the sum of H_100(sqrt(beta)) for beta in T.
    Give the last 15 digits of your answer.

URL: https://projecteuler.net/problem=656
"""
from typing import Any

euler_problem: int = 656
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'nBWR7EQomlf8XSQbSAw07A=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
