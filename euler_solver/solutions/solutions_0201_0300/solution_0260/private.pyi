#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 260: Stone Game.

Problem Statement:
    A game is played with three piles of stones and two players. On each player's
    turn, the player may remove one or more stones from the piles. However, if
    the player takes stones from more than one pile, then the same number of
    stones must be removed from each of the selected piles.
    In other words, the player chooses some N > 0 and removes:
        N stones from any single pile; or
        N stones from each of any two piles (2N total); or
        N stones from each of the three piles (3N total).
    The player taking the last stone(s) wins the game.
    A winning configuration is one where the first player can force a win. For
    example, (0,0,13), (0,11,11), and (5,5,5) are winning configurations because
    the first player can immediately remove all stones.
    A losing configuration is one where the second player can force a win, no
    matter what the first player does. For example, (0,1,2) and (1,3,3) are
    losing configurations: any legal move leaves a winning configuration for the
    second player.
    Consider all losing configurations (x_i, y_i, z_i) where x_i <= y_i <= z_i
    <= 100. We can verify that sum(x_i + y_i + z_i) = 173895 for these.
    Find sum(x_i + y_i + z_i) where (x_i, y_i, z_i) ranges over the losing
    configurations with x_i <= y_i <= z_i <= 1000.

Solution Approach:
    This is an impartial normal-play game. Use the Sprague–Grundy theorem and
    compute Grundy (nimber) values for all sorted triples (x,y,z) with 0 <= x <=
    y <= z <= L where L is the limit (1000). For each state, enumerate legal
    moves by choosing N>=1 and subtracting N from one, two, or three coordinates
    (keeping nonnegative results); collect reachable nimbers and take mex.
    Use dynamic programming in increasing order of x+y+z and exploit symmetry
    x<=y<=z to reduce states. Naive complexity is roughly O(L^4) but symmetry
    and incremental mex can make it feasible for L=1000 with careful coding.
    Expected resources: time roughly polynomial in L^3 with moderate memory.

Answer: ...
URL: https://projecteuler.net/problem=260
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 260
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 1000}},
    {'category': 'extra', 'input': {'max_limit': 2000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_stone_game_p0260_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))