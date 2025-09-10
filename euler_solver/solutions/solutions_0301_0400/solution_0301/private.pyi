#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 301: Nim.

Problem Statement:
    Nim is a game played with heaps of stones, where two players take it in
    turn to remove any number of stones from any heap until no stones remain.

    We'll consider the three-heap normal-play version of Nim, which works as
    follows:
    At the start of the game there are three heaps of stones.
    On each player's turn, the player may remove any positive number of stones
    from any single heap.
    The first player unable to move (because no stones remain) loses.

    If (n1,n2,n3) indicates a Nim position consisting of heaps of size n1, n2,
    and n3, then there is a simple function, which you may look up or attempt
    to deduce for yourself, X(n1,n2,n3) that returns:
    zero if, with perfect strategy, the player about to move will eventually
    lose; or
    non-zero if, with perfect strategy, the player about to move will
    eventually win.

    For example X(1,2,3) = 0 because, no matter what the current player does,
    the opponent can respond with a move that leaves two heaps of equal size,
    at which point every move by the current player can be mirrored by the
    opponent until no stones remain; so the current player loses. To
    illustrate:
    current player moves to (1,2,1)
    opponent moves to (1,0,1)
    current player moves to (0,0,1)
    opponent moves to (0,0,0), and so wins.

    For how many positive integers n <= 2^30 does X(n,2n,3n) = 0 ?

Solution Approach:
    Use the Nim losing-position criterion: a position is losing iff the bitwise
    xor of heap sizes is zero. Here we need to count n <= N with n ^ 2n ^ 3n = 0.
    Key ideas: analyze binary representations, treat carries when computing 3n
    = n + 2n, and perform a digit-DP over bits to count valid n efficiently.
    This yields an O(log N) or O((log N)*constant) dynamic-programming solution
    using bitwise/state transitions and combinatorics to count choices.

Answer: ...
URL: https://projecteuler.net/problem=301
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 301
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 1073741824}},
    {'category': 'extra', 'input': {'max_limit': 4294967296}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_nim_p0301_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))