#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 161: Triominoes.

Problem Statement:
    A triomino is a shape consisting of three squares joined via the edges.
    There are two basic forms.

    If all possible orientations are taken into account there are six.

    Any n by m grid for which n * m is divisible by 3 can be tiled with
    triominoes.

    If we consider tilings that can be obtained by reflection or rotation
    from another tiling as different there are 41 ways a 2 by 9 grid can be
    tiled with triominoes.

    In how many ways can a 9 by 12 grid be tiled in this way by
    triominoes?

URL: https://projecteuler.net/problem=161
"""
from typing import Any

euler_problem: int = 161
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'rows': 2, 'cols': 9}, 'answer': None},
    {'category': 'main', 'input': {'rows': 9, 'cols': 12}, 'answer': None},
    {'category': 'extra', 'input': {'rows': 6, 'cols': 6}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
