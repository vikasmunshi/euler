#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 227: The Chase.

Problem Statement:
    The Chase is a game played with two dice and an even number of players.
    The players sit around a table and the game begins with two opposite
    players having one die each. On each turn, the two players with a die roll it.

    If the player rolls 1, then the die passes to the neighbour on the left.
    If the player rolls 6, then the die passes to the neighbour on the right.
    Otherwise, the player keeps the die for the next turn.

    The game ends when one player has both dice after they have been rolled and
    passed; that player has then lost.

    In a game with 100 players, what is the expected number of turns the game
    lasts?
    Give your answer rounded to ten significant digits.

URL: https://projecteuler.net/problem=227
"""
from typing import Any

euler_problem: int = 227
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_players': 4}, 'answer': None},
    {'category': 'main', 'input': {'num_players': 100}, 'answer': None},
    {'category': 'extra', 'input': {'num_players': 200}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
