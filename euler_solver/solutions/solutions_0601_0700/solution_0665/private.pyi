#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 665: Proportionate Nim.

Problem Statement:
    Two players play a game with two piles of stones, alternating turns.

    On each turn, the corresponding player chooses a positive integer n and does one of the
    following:
        removes n stones from one pile;
        removes n stones from both piles; or
        removes n stones from one pile and 2n stones from the other pile.

    The player who removes the last stone wins.

    We denote by (n,m) the position in which the piles have n and m stones remaining. Note
    that (n,m) is considered to be the same position as (m,n).

    Then, for example, if the position is (2,6), the next player may reach the following
    positions:
    (0,2), (0,4), (0,5), (0,6), (1,2), (1,4), (1,5), (1,6), (2,2), (2,3), (2,4), (2,5).

    A position is a losing position if the player to move next cannot force a win. For example,
    (1,3), (2,6), (4,5) are the first few losing positions.

    Let f(M) be the sum of n+m for all losing positions (n,m) with n <= m and n+m <= M. For
    example, f(10) = 21, by considering the losing positions (1,3), (2,6), (4,5).

    You are given that f(100) = 1164 and f(1000) = 117002.

    Find f(10^7).

Solution Approach:
    Use combinatorial game theory to identify losing positions (P-positions) by defining
    reachable moves and their structure.
    Employ dynamic programming or mathematical characterization (possibly involving number
    theory or combinatorics) to efficiently enumerate losing positions up to M.
    Optimize with pruning and symmetry (positions (n,m) and (m,n) are equivalent).
    Aim for an O(M log M) or better approach by leveraging algebraic properties.

Answer: ...
URL: https://projecteuler.net/problem=665
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 665
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 10000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_proportionate_nim_p0665_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))