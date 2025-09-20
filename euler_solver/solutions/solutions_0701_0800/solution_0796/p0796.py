#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 796: A Grand Shuffle.

Problem Statement:
    A standard 52 card deck comprises thirteen ranks in four suits. However,
    modern decks have two additional Jokers, which neither have a suit nor a
    rank, for a total of 54 cards. If we shuffle such a deck and draw cards
    without replacement, then we would need, on average, approximately
    29.05361725 cards so that we have at least one card for each rank.

    Now, assume you have 10 such decks, each with a different back design.
    We shuffle all 10 × 54 cards together and draw cards without replacement.
    What is the expected number of cards needed so every suit, rank and deck
    design have at least one card?

    Give your answer rounded to eight places after the decimal point.

URL: https://projecteuler.net/problem=796
"""
from typing import Any

euler_problem: int = 796
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'WHAI/uugfgJzAEtMxtvaVCrFIAgqfFNV'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
