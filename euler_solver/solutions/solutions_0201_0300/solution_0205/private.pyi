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

Solution Approach:
    Compute each player's probability mass function (PMF) for the sum of their
    dice. Use dynamic programming or repeated convolution of the single-die PMF
    to get the distribution for multiple dice.
    Then compute P(Peter > Colin) = sum_s P(Peter=s) * P(Colin < s) by using the
    cumulative distribution of Colin.
    This is efficient for the given sizes; time roughly proportional to the
    product of the number of dice and the range of possible sums (polynomial).
    Use integer arithmetic for counts and convert to a probability at the end.

Answer: ...
URL: https://projecteuler.net/problem=205
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 205
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'p_dice': 1, 'p_sides': 4, 'c_dice': 1, 'c_sides': 6, 'precision': 7}},
    {'category': 'main', 'input': {'p_dice': 9, 'p_sides': 4, 'c_dice': 6, 'c_sides': 6, 'precision': 7}},
    {'category': 'extra', 'input': {'p_dice': 12, 'p_sides': 4, 'c_dice': 9, 'c_sides': 6, 'precision': 7}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_dice_game_p0205_s0(*, p_dice: int, p_sides: int, c_dice: int, c_sides: int, precision: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))