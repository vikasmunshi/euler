#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 367: Bozo Sort.

Problem Statement:
    Bozo sort, not to be confused with bogo sort, repeatedly checks whether the
    input sequence is sorted and, if not, swaps two randomly chosen elements.
    This is repeated until the sequence is sorted.

    If we consider all permutations of the first 4 natural numbers as input,
    the expected number of swaps, averaged over all 4! input sequences, is
    24.75. The already sorted sequence takes 0 steps.

    This problem uses a variant: if the sequence is not sorted we pick three
    elements uniformly at random and apply a uniformly random permutation of
    these three elements (all 3! = 6 permutations equally likely). The already
    sorted sequence takes 0 steps. For n = 4 the averaged expected number of
    such shuffles is 27.5.

    Consider all permutations of the first 11 natural numbers. Averaged over
    all 11! input sequences, what is the expected number of shuffles this
    algorithm will perform?

    Give your answer rounded to the nearest integer.

URL: https://projecteuler.net/problem=367
"""
from typing import Any

euler_problem: int = 367
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 11}, 'answer': None},
    {'category': 'extra', 'input': {'n': 12}, 'answer': None},
]
encrypted: str = (
    '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'
    'tWzfH4r8x4SAqxgi'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
