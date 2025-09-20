#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 868: Belfry Maths.

Problem Statement:
    There is a method that is used by Bell ringers to generate all variations of
    the order that bells are rung.

    The same method can be used to create all permutations of a set of letters.
    Consider the letters to be permuted initially in order from smallest to
    largest. At each step swap the largest letter with the letter on its left or
    right whichever generates a permutation that has not yet been seen. If neither
    gives a new permutation then try the next largest letter and so on. This
    procedure continues until all permutations have been generated.

    For example, 3 swaps are required to reach the permutation CBA when starting
    with ABC.
    The swaps are ABC -> ACB -> CAB -> CBA.
    Also 59 swaps are required to reach BELFRY when starting with these letters
    in alphabetical order.

    Find the number of swaps that are required to reach NOWPICKBELFRYMATHS when
    starting with these letters in alphabetical order.

URL: https://projecteuler.net/problem=868
"""
from typing import Any

euler_problem: int = 868
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'target': 'CBA'}, 'answer': None},
    {'category': 'main', 'input': {'target': 'NOWPICKBELFRYMATHS'}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
