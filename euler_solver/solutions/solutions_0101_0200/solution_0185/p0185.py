#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 185: Number Mind.

Problem Statement:
    The game Number Mind is a variant of the well known game Master Mind.
    Instead of coloured pegs, you have to guess a secret sequence of digits.
    After each guess you're only told in how many places you've guessed the
    correct digit. So, if the sequence was 1234 and you guessed 2036, you'd be
    told that you have one correct digit; however, you would NOT be told that
    you also have another digit in the wrong place.

    For instance, given the following guesses for a 5-digit secret sequence,
    90342 ;2 correct
    70794 ;0 correct
    39458 ;2 correct
    34109 ;1 correct
    51545 ;2 correct
    12531 ;1 correct

    The correct sequence 39542 is unique.

    Based on the following guesses,
    5616185650518293 ;2 correct
    3847439647293047 ;1 correct
    5855462940810587 ;3 correct
    9742855507068353 ;3 correct
    4296849643607543 ;3 correct
    3174248439465858 ;1 correct
    4513559094146117 ;2 correct
    7890971548908067 ;3 correct
    8157356344118483 ;1 correct
    2615250744386899 ;2 correct
    8690095851526254 ;3 correct
    6375711915077050 ;1 correct
    6913859173121360 ;1 correct
    6442889055042768 ;2 correct
    2321386104303845 ;0 correct
    2326509471271448 ;2 correct
    5251583379644322 ;2 correct
    1748270476758276 ;3 correct
    4895722652190306 ;1 correct
    3041631117224635 ;3 correct
    1841236454324589 ;3 correct
    2659862637316867 ;2 correct

    Find the unique 16-digit secret sequence.

URL: https://projecteuler.net/problem=185
"""
from typing import Any

euler_problem: int = 185
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'EFFMAk80KtH0qPZWpFv3F/yqf6Q='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
