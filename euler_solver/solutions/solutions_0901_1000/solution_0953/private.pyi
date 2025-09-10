#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 953: Factorisation Nim.

Problem Statement:
    In the classical game of Nim two players take turns removing stones
    from piles. A player may remove any positive number of stones from a
    single pile. If there are no remaining stones, the next player to move
    loses.

    In Factorisation Nim the initial position of the game is chosen according
    to the prime factorisation of a given natural number n by setting a pile
    for each prime factor, including multiplicity. For example, if n=12=2 x 2 x 3
    the game starts with three piles: two piles with two stones and one pile
    with three stones.

    It can be verified that the first player to move loses for n=1 and for
    n=70, assuming both players play optimally.

    Let S(N) be the sum of n for 1 <= n <= N such that the first player to
    move loses, assuming both players play optimally. You are given
    S(10) = 14 and S(100) = 455.

    Find S(10^14). Give your answer modulo 10^9 + 7.

Solution Approach:
    Model the game state as the multiset of prime factors of n. Nim theory
    relates losing positions to nim-sum zero. The factor piles correspond to
    prime factors, but note that pile sizes are the prime values themselves,
    not frequencies.

    The problem reduces to identifying n where the nim-sum of their prime
    factors (including multiplicities) is zero.

    Key ideas: combinatorics, number theory, prime factorization, nim-sum.

    Efficient factorization and summation with modulo arithmetic are required.
    Precomputation and bitwise nim-sum computations are critical due to large N.

Answer: ...
URL: https://projecteuler.net/problem=953
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 953
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 10**14}},
    {'category': 'extra', 'input': {'max_limit': 10**15}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_factorisation_nim_p0953_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
