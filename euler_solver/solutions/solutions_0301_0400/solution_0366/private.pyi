#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 366: Stone Game III.

Problem Statement:
    Two players, Anton and Bernhard, are playing the following game.
    There is one pile of n stones.
    The first player may remove any positive number of stones, but not the whole pile.
    Thereafter, each player may remove at most twice the number of stones his opponent
    took on the previous move.
    The player who removes the last stone wins.

    E.g. n = 5.
    If the first player takes anything more than one stone the next player will be able
    to take all remaining stones.
    If the first player takes one stone, leaving four, his opponent will take also one
    stone, leaving three stones.
    The first player cannot take all three because he may take at most 2 x 1 = 2 stones.
    So let's say he takes also one stone, leaving 2. The second player can take the
    two remaining stones and wins.
    So 5 is a losing position for the first player.
    For some winning positions there is more than one possible move for the first
    player. E.g. when n = 17 the first player can remove one or four stones.

    Let M(n) be the maximum number of stones the first player can take from a winning
    position at his first turn and M(n) = 0 for any other position.

    Sum M(n) for n <= 100 is 728.

    Find sum M(n) for n <= 1000000000000000000. Give your answer modulo 100000000.

Solution Approach:
    Model this as an impartial take-and-limit game and classify positions as winning
    or losing (P-positions) using the recurrence determined by the doubling rule.
    Determine M(n) from the first legal winning moves. Look for structure in the
    sequence of P-positions (recurrence or Beatty-like decomposition) to compress
    ranges and derive closed-form counts. Use interval grouping and fast recurrence
    evaluation to sum M(n) up to 10^18 in roughly polylog or sublinear time in the
    number of ranges; space complexity is small (O(1) to O(log n)).

Answer: ...
URL: https://projecteuler.net/problem=366
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 366
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100, 'mod': 100000000}},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000, 'mod': 100000000}},
    {'category': 'extra', 'input': {'max_limit': 1000000000000, 'mod': 100000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_stone_game_iii_p0366_s0(*, max_limit: int, mod: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))