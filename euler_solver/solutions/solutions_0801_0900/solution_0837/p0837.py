#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 837: Amidakuji.

Problem Statement:
    Amidakuji (Japanese: 阿弥陀籤) is a method for producing a random permutation
    of a set of objects.

    In the beginning, a number of parallel vertical lines are drawn, one for each
    object. Then a specified number of horizontal rungs are added, each lower than
    any previous rungs. Each rung is drawn as a line segment spanning a randomly
    selected pair of adjacent vertical lines.

    For example, with three objects (A, B, C) and six rungs, the coloured lines show
    how to form the permutation. For each object, starting from the top of its vertical
    line, trace downwards but follow any rung encountered along the way, and record
    which vertical line you end up on. The example shown results in the identity:
    A→A, B→B, C→C.

    Let a(m, n) be the number of different three-object Amidakujis that have m rungs
    between A and B, and n rungs between B and C, and whose outcome is the identity
    permutation. For example, a(3, 3) = 2 because the Amidakuji and its mirror image
    are the only ones with the required property.

    It is given that a(123, 321) ≡ 172633303 (mod 1234567891).

    Find a(123456789, 987654321). Give your answer modulo 1234567891.

URL: https://projecteuler.net/problem=837
"""
from typing import Any

euler_problem: int = 837
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 3, 'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'m': 123456789, 'n': 987654321}, 'answer': None},
]
encrypted: str = (
    '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'
    'CJ39gfOaDCQAX2LLeFlVyWIVl5ouaNk2VEAxuw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
