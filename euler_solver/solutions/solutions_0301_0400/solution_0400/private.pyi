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

Solution Approach:
    Use combinatorial game theory and recursive structure of Fibonacci trees.
    Analyze the game's Grundy values or winning positions using the recursive
    definition T(k) = root with children T(k-1) and T(k-2).
    Utilize memoization and mathematical properties of Fibonacci sequences to
    efficiently compute f(10000).
    Modular arithmetic or string manipulation to handle last 18 digits.

Answer: ...
URL: https://projecteuler.net/problem=400
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 400
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 5}},
    {'category': 'main', 'input': {'k': 10000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_fibonacci_tree_game_p0400_s0(*, k: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))