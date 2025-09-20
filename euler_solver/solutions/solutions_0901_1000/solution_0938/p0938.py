#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 938: Exhausting a Colour.

Problem Statement:
    A deck of cards contains R red cards and B black cards.
    A card is chosen uniformly randomly from the deck and removed.
    A second card is then chosen uniformly randomly from the cards remaining and removed.

    If both cards are red, they are discarded.
    If both cards are black, they are both put back in the deck.
    If they are different colours, the red card is put back in the deck and the black card is discarded.

    Play ends when all the remaining cards in the deck are the same colour and let P(R,B) be
    the probability that this colour is black.

    You are given P(2,2) = 0.4666666667, P(10,9) = 0.4118903397 and P(34,25) = 0.3665688069.

    Find P(24690,12345). Give your answer with 10 digits after the decimal point.

URL: https://projecteuler.net/problem=938
"""
from typing import Any

euler_problem: int = 938
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'R': 24690, 'B': 12345}, 'answer': None},
    {'category': 'dev', 'input': {'R': 2, 'B': 2}, 'answer': None},
    {'category': 'extra', 'input': {'R': 34, 'B': 25}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
