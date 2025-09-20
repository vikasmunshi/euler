#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 205: Dice Game.

Problem Statement:
    Peter has nine four-sided (pyramidal) dice, each with faces numbered 1, 2,
    3, 4.
    Colin has six six-sided (cubic) dice, each with faces numbered 1, 2, 3, 4,
    5, 6.

    Peter and Colin roll their dice and compare totals: the highest total wins.
    The result is a draw if the totals are equal.

    What is the probability that Pyramidal Peter beats Cubic Colin? Give your
    answer rounded to seven decimal places in the form 0.abcdefg.

URL: https://projecteuler.net/problem=205
"""
from typing import Any

euler_problem: int = 205
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'p_dice': 1, 'p_sides': 4, 'c_dice': 1, 'c_sides': 6, 'precision': 7},
     'answer': None},
    {'category': 'main', 'input': {'p_dice': 9, 'p_sides': 4, 'c_dice': 6, 'c_sides': 6, 'precision': 7},
     'answer': None},
    {'category': 'extra', 'input': {'p_dice': 12, 'p_sides': 4, 'c_dice': 9, 'c_sides': 6, 'precision': 7},
     'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
