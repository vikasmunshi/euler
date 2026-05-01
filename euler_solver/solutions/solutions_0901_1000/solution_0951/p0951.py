#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 951: A Game of Chance.

Problem Statement:
    Two players play a game using a deck of 2n cards: n red and n black. Initially the deck is
    shuffled into one of the C(2n, n) possible starting configurations. Play then proceeds,
    alternating turns, where a player follows two steps on each turn:

        1. Remove the top card from the deck, noting its colour.
        2. If there is a next card and it is the same colour as the previous card, toss a fair coin.
           If heads, remove that card as well; else leave it on top.

    The player who removes the final card from the deck wins the game.

    Some starting configurations give an advantage to one player; some are fair, with both players
    having exactly 50% chance to win. For example, n=2 has four fair configurations:
    RRBB, BBRR, RBBR, BRRB. The other two, RBRB and BRBR, guarantee a win for the second player.

    Define F(n) as the number of fair starting configurations. Given F(2)=4 and F(8)=11892, find F(26).

URL: https://projecteuler.net/problem=951
"""
from typing import Any

euler_problem: int = 951
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 26}, 'answer': None},
    {'category': 'extra', 'input': {'n': 28}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
