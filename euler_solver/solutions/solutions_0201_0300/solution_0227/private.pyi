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

Solution Approach:
    Model as an absorbing Markov chain on the relative separation of the two dice
    (use rotational symmetry). States are distances between dice (1..N/2).
    Compute expected absorption time from the starting distance (opposite players)
    by solving linear equations for mean hitting times or by linear-algebraic
    methods (solve (I-Q)^{-1} * 1). Time ~ O(m^3) for dense solver, m~N/2 states.

Answer: ...
URL: https://projecteuler.net/problem=227
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 227
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_players': 4}},
    {'category': 'main', 'input': {'num_players': 100}},
    {'category': 'extra', 'input': {'num_players': 200}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_the_chase_p0227_s0(*, num_players: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))