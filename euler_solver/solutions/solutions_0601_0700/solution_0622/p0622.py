#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 622: Riffle Shuffles.

Problem Statement:
    A riffle shuffle is executed as follows: a deck of cards is split into two equal halves,
    with the top half taken in the left hand and the bottom half taken in the right hand.
    Next, the cards are interleaved exactly, with the top card in the right half inserted just
    after the top card in the left half, the 2nd card in the right half just after the 2nd card
    in the left half, etc. (Note that this process preserves the location of the top and bottom
    card of the deck)

    Let s(n) be the minimum number of consecutive riffle shuffles needed to restore a deck of
    size n to its original configuration, where n is a positive even number.

    Amazingly, a standard deck of 52 cards will first return to its original configuration
    after only 8 perfect shuffles, so s(52) = 8. It can be verified that a deck of 86 cards
    will also return to its original configuration after exactly 8 shuffles, and the sum of all
    values of n that satisfy s(n) = 8 is 412.

    Find the sum of all values of n that satisfy s(n) = 60.

URL: https://projecteuler.net/problem=622
"""
from typing import Any

euler_problem: int = 622
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'s_target': 8, 'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'s_target': 60}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
