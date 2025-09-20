#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 856: Waiting for a Pair.

Problem Statement:
    A standard 52-card deck comprises 13 ranks in four suits. A pair is a set of two cards
    of the same rank.

    Cards are drawn, without replacement, from a well shuffled 52-card deck waiting for
    consecutive cards that form a pair. For example, the probability of finding a pair in
    the first two draws is 1/17.

    Cards are drawn until either such a pair is found or the pack is exhausted waiting for
    one. In the latter case we say that all 52 cards were drawn.

    Find the expected number of cards that were drawn. Give your answer rounded to eight
    places after the decimal point.

URL: https://projecteuler.net/problem=856
"""
from typing import Any

euler_problem: int = 856
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'MbRnqul/iPjKuox4TTD4dwbgD1pzjfTV'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
