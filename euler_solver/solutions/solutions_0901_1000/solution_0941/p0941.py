#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 941: de Bruijn's Combination Lock.

Problem Statement:
    de Bruijn has a digital combination lock with k buttons numbered 0 to k-1
    where k ≤ 10. The lock opens when the last n buttons pressed match the
    preset combination.

    Unfortunately he has forgotten the combination. He creates a sequence of
    these digits which contains every possible combination of length n. Then
    by pressing the buttons in this order he is sure to open the lock.

    Consider all sequences of shortest possible length that contains every
    possible combination of the digits.
    Denote by C(k, n) the lexicographically smallest of these.

    For example, C(3, 2) = 0010211220.

    Define the sequence a_n by a_0 = 0 and
    a_n = (920461 a_(n-1) + 800217387569) mod 10^12 for n > 0.
    Interpret each a_n as a 12-digit combination, adding leading zeros if needed.

    Given a positive integer N, consider the order the combinations a_1,...,a_N
    appear in C(10, 12).
    Denote by p_n the place, numbered 1,...,N, in which a_n appears out of these.
    Define F(N) = sum_{n=1}^N p_n * a_n.

    For example, the combination a_1 = 800217387569 is entered before a_2 =
    696996536878.
    Therefore:
    F(2) = 1 * 800217387569 + 2 * 696996536878 = 2194210461325.
    You are also given F(10) = 32698850376317.

    Find F(10^7). Give your answer modulo 1234567891.

URL: https://projecteuler.net/problem=941
"""
from typing import Any

euler_problem: int = 941
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 2}, 'answer': None},
    {'category': 'main', 'input': {'N': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
