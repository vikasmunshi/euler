#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 400: Fibonacci Tree Game.

Problem Statement:
    A Fibonacci tree is a binary tree recursively defined as:
        T(0) is the empty tree.
        T(1) is the binary tree with only one node.
        T(k) consists of a root node that has T(k-1) and T(k-2) as children.

    On such a tree two players play a take-away game. On each turn a player selects
    a node and removes that node along with the subtree rooted at that node.
    The player who is forced to take the root node of the entire tree loses.

    Here are the winning moves of the first player on the first turn for T(k) from
    k=1 to k=6.

    Let f(k) be the number of winning moves of the first player (i.e. the moves for
    which the second player has no winning strategy) on the first turn of the game
    when this game is played on T(k).

    For example, f(5) = 1 and f(10) = 17.

    Find f(10000). Give the last 18 digits of your answer.

URL: https://projecteuler.net/problem=400
"""
from typing import Any

euler_problem: int = 400
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 5}, 'answer': None},
    {'category': 'main', 'input': {'k': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
