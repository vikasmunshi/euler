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

URL: https://projecteuler.net/problem=260
"""
from typing import Any

euler_problem: int = 260
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 2000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
