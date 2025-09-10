#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 882: Removing Bits.

Problem Statement:
    Dr. One and Dr. Zero are playing the following partisan game.
    The game begins with one 1, two 2's, three 3's, ..., n n's.
    Starting with Dr. One, they make moves in turn.
    Dr. One chooses a number and changes it by removing a 1 from its binary expansion.
    Dr. Zero chooses a number and changes it by removing a 0 from its binary expansion.
    The player that is unable to move loses.
    Note that leading zeros are not allowed in any binary expansion; in particular nobody
    can make a move on the number 0.

    They soon realize that Dr. Zero can never win the game. In order to make it more
    interesting, Dr. Zero is allowed to "skip the turn" several times, i.e. passing the
    turn back to Dr. One without making a move.

    For example, when n = 2, Dr. Zero can win the game if allowed to skip 2 turns.
    A sample game:
    [1, 2, 2] -> Dr. One -> [1, 0, 2] -> Dr. Zero -> [1, 0, 1] -> Dr. One -> [1, 0, 0]
    -> skip by Dr. Zero -> [1, 0, 0] -> Dr. One -> [0, 0, 0] -> skip by Dr. Zero -> [0, 0, 0].

    Let S(n) be the minimal number of skips needed so that Dr. Zero has a winning strategy.
    For example, S(2) = 2, S(5) = 17, S(10) = 64.

    Find S(10^5).

Solution Approach:
    Model as a combinatorial game with binary expansions and moves removing bits.
    Use impartial game theory, Sprague-Grundy theorem with state encoding.
    Consider turns and skips as additional states within the game tree.
    Optimization by precomputation and pattern detection is crucial for large n.
    Efficiently count bit patterns and calculate minimal skips for winning strategy.
    Expected complexity involves dynamic programming and combinatorics on bit strings.

Answer: ...
URL: https://projecteuler.net/problem=882
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 882
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}},
    {'category': 'dev', 'input': {'n': 5}},
    {'category': 'main', 'input': {'n': 100000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_removing_bits_p0882_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))