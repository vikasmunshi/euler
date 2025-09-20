#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 595: Incremental Random Sort.

Problem Statement:
    A deck of cards numbered from 1 to n is shuffled randomly such that each
    permutation is equally likely.

    The cards are to be sorted into ascending order using the following technique:

        1. Look at the initial sequence of cards. If it is already sorted, then
           there is no need for further action. Otherwise, if any subsequences
           of cards happen to be in the correct place relative to one another
           (ascending with no gaps), then those subsequences are fixed by
           attaching the cards together. For example, with 7 cards initially in
           the order 4123756, the cards labelled 1, 2 and 3 would be attached
           together, as would 5 and 6.

        2. The cards are 'shuffled' by being thrown into the air, but note that
           any correctly sequenced cards remain attached, so their orders are
           maintained. The cards (or bundles of attached cards) are then picked
           up randomly. You should assume that this randomisation is unbiased,
           despite the fact that some cards are single, and others are grouped
           together.

        3. Repeat steps 1 and 2 until the cards are sorted.

    Let S(n) be the expected number of shuffles needed to sort the cards. Since
    the order is checked before the first shuffle, S(1) = 0. You are given that
    S(2) = 1, and S(5) = 4213/871.

    Find S(52), and give your answer rounded to 8 decimal places.

URL: https://projecteuler.net/problem=595
"""
from typing import Any

euler_problem: int = 595
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 52}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
