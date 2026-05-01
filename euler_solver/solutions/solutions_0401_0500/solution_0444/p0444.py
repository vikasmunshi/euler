#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 444: The Roundtable Lottery.

Problem Statement:
    A group of p people decide to sit down at a round table and play a lottery-ticket
    trading game. Each person starts off with a randomly-assigned, unscratched lottery
    ticket. Each ticket, when scratched, reveals a whole-pound prize ranging anywhere
    from £1 to £p, with no two tickets alike. The goal of the game is for all of the
    players to maximize the winnings of the ticket they hold upon leaving the game.

    An arbitrary person is chosen to be the first player. Going around the table, each
    player has only one of two options:
        1. The player can choose to scratch the ticket and reveal its worth to everyone
           at the table.
        2. If the player's ticket is unscratched, then the player may trade it with a
           previous player's scratched ticket, and then leaves the game with that ticket.
           The previous player then scratches the newly-acquired ticket and reveals its
           worth to everyone at the table.

    The game ends once all tickets have been scratched. All players still remaining at the
    table must leave with their currently-held tickets.

    Assume that players will use the optimal strategy for maximizing the expected value
    of their ticket winnings.

    Let E(p) represent the expected number of players left at the table when the game ends
    in a game consisting of p players.
    E.g. E(111) = 5.2912 when rounded to 5 significant digits.

    Let S_1(N) = sum_{p = 1}^{N} E(p).
    Let S_k(N) = sum_{p = 1}^{N} S_{k-1}(p) for k > 1.

    Find S_{20}(10^14) and write the answer in scientific notation rounded to 10 significant
    digits. Use a lowercase e to separate mantissa and exponent. For example, the answer
    for S_3(100) would be 5.983679014e5.

URL: https://projecteuler.net/problem=444
"""
from typing import Any

euler_problem: int = 444
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'Uvli+nPv6LE4NZQxufmzKzNCcBo='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
