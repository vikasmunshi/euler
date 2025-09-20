#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 928: Cribbage.

Problem Statement:
    This problem is based on (but not identical to) the scoring for the card game
    Cribbage.

    Consider a normal pack of 52 cards. A Hand is a selection of one or more of these cards.

    For each Hand the Hand score is the sum of the values of the cards in the Hand where
    the value of Aces is 1 and the value of court cards (Jack, Queen, King) is 10.

    The Cribbage score is obtained for a Hand by adding together the scores for:

        Pairs. A pair is two cards of the same rank. Every pair is worth 2 points.

        Runs. A run is a set of at least 3 cards whose ranks are consecutive, e.g. 9, 10,
        Jack. Note that Ace is never high, so Queen, King, Ace is not a valid run. The
        number of points for each run is the size of the run. All locally maximum runs are
        counted. For example, 2, 3, 4, 5, 7, 8, 9 the two runs of 2, 3, 4, 5 and 7, 8, 9
        are counted but not 2, 3, 4 or 3, 4, 5.

        Fifteens. A fifteen is a combination of cards that has value adding to 15. Every
        fifteen is worth 2 points. For this purpose the value of the cards is the same as
        in the Hand Score.

    For example, (5♠, 5♣, 5♦, K♥) has a Cribbage score of 14 as there are four ways that
    fifteen can be made and also three pairs can be made.

    The example (A♦, A♥, 2♣, 3♥, 4♣, 5♠) has a Cribbage score of 16: two runs of five
    worth 10 points, two ways of getting fifteen worth 4 points and one pair worth 2
    points. In this example the Hand score is equal to the Cribbage score.

    Find the number of Hands in a normal pack of cards where the Hand score is equal to
    the Cribbage score.

URL: https://projecteuler.net/problem=928
"""
from typing import Any

euler_problem: int = 928
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'sw89sA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
