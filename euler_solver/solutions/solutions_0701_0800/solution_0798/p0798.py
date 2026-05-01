#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 798: Card Stacking Game.

Problem Statement:
    Two players play a game with a deck of cards which contains s suits with each suit
    containing n cards numbered from 1 to n.

    Before the game starts, a set of cards (which may be empty) is picked from the deck
    and placed face-up on the table, with no overlap. These are called the visible cards.

    The players then make moves in turn.
    A move consists of choosing a card X from the rest of the deck and placing it face-up
    on top of a visible card Y, subject to the following restrictions:
        - X and Y must be the same suit;
        - the value of X must be larger than the value of Y.
    The card X then covers the card Y and replaces Y as a visible card.
    The player unable to make a valid move loses and play stops.

    Let C(n, s) be the number of different initial sets of cards for which the first player
    will lose given best play for both players.

    For example, C(3, 2) = 26 and C(13, 4) ≡ 540318329 (mod 1,000,000,007).

    Find C(10^7, 10^7). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=798
"""
from typing import Any

euler_problem: int = 798
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3, 's': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000, 's': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
