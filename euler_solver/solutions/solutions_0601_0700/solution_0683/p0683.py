#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 683: The Chase II.

Problem Statement:
    Consider the following variant of "The Chase" game. This game is played between n players
    sitting around a circular table using two dice. It consists of n-1 rounds, and at the end
    of each round one player is eliminated and has to pay a certain amount of money into a pot.
    The last player remaining is the winner and receives the entire contents of the pot.

    At the beginning of a round, each die is given to a randomly selected player. A round then
    consists of a number of turns.

    During each turn, each of the two players with a die rolls it. If a player rolls a 1 or a 2,
    the die is passed to the neighbour on the left; if the player rolls a 5 or a 6, the die is
    passed to the neighbour on the right; otherwise, the player keeps the die for the next turn.

    The round ends when one player has both dice at the beginning of a turn. At which point that
    player is immediately eliminated and has to pay s^2 where s is the number of completed turns
    in this round. Note that if both dice happen to be handed to the same player at the beginning
    of a round, then no turns are completed, so the player is eliminated without having to pay
    any money into the pot.

    Let G(n) be the expected amount that the winner will receive. For example G(5) is approximately
    96.544, and G(50) is 2.82491788e6 in scientific notation rounded to 9 significant digits.

    Find G(500), giving your answer in scientific notation rounded to 9 significant digits.

URL: https://projecteuler.net/problem=683
"""
from typing import Any

euler_problem: int = 683
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}, 'answer': None},
    {'category': 'main', 'input': {'n': 500}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
    'vl2cBBeaokbQXXn6IaQV69i/anNKgHds'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
