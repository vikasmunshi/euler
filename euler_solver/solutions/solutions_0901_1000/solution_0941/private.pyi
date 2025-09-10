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

Solution Approach:
    Use combinatorics and properties of de Bruijn sequences to locate the
    index positions of given combinations.
    Efficiently generate or simulate lexicographically minimal sequences with
    large parameters.
    Employ modular arithmetic and recurrence relations to handle sequence a_n.
    Use indexing and numeric pattern recognition to calculate F(N) without
    enumerating full sequences.
    Algorithmic complexity is critical due to large N (10^7) and length (12 digits).

Answer: ...
URL: https://projecteuler.net/problem=941
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 941
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 2}},
    {'category': 'main', 'input': {'N': 10000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_de_bruijns_combination_lock_p0941_s0(*, N: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
