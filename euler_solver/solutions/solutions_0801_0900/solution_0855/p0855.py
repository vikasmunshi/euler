#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 855: Delphi Paper.

Problem Statement:
    Given two positive integers a,b, Alex and Bianca play a game in ab rounds.
    They begin with a square piece of paper of side length 1.

    In each round Alex divides the current rectangular piece of paper into a × b
    pieces using a−1 horizontal cuts and b−1 vertical ones. The cuts do not need
    to be evenly spaced. Moreover, a piece can have zero width/height when a cut
    coincides with another cut or the edge of the paper. The pieces are then numbered
    1, 2, ..., ab starting from the left top corner, moving from left to right and
    starting from the left of the next row when a row is finished.

    Then Bianca chooses one of the pieces for the game to continue on. However,
    Bianca must not choose a piece with a number she has already chosen during the
    game.

    Bianca wants to minimize the area of the final piece of paper while Alex wants
    to maximize it. Let S(a,b) be the area of the final piece assuming optimal play.

    For example, S(2,2) = 1/36 and S(2,3) = 1/1800 ≈ 5.5555555556e-4.

    Find S(5,8). Give your answer in scientific notation rounded to ten significant
    digits after the decimal point. Use a lowercase e to separate the mantissa
    and the exponent.

URL: https://projecteuler.net/problem=855
"""
from typing import Any

euler_problem: int = 855
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'a': 5, 'b': 8}, 'answer': None},
]
encrypted: str = (
    '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'
    'Qo5uaDUBNYQ='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
