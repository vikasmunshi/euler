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

URL: https://projecteuler.net/problem=301
"""
from typing import Any

euler_problem: int = 301
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1073741824}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 4294967296}, 'answer': None},
]
encrypted: str = (
    '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'
    'N0qv6Q=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
