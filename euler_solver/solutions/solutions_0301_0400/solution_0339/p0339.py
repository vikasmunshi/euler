#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 339: Peredur Fab Efrawg.

Problem Statement:
    "And he came towards a valley, through which ran a river; and the borders
    of the valley were wooded, and on each side of the river were level
    meadows. And on one side of the river he saw a flock of white sheep, and
    on the other a flock of black sheep. And whenever one of the white sheep
    bleated, one of the black sheep would cross over and become white; and when
    one of the black sheep bleated, one of the white sheep would cross over and
    become black."
    (Source: en.wikisource.org)

    Initially each flock consists of n sheep. Each sheep (regardless of colour)
    is equally likely to be the next sheep to bleat. After a sheep has bleated
    and a sheep from the other flock has crossed over, Peredur may remove a
    number of white sheep in order to maximize the expected final number of
    black sheep. Let E(n) be the expected final number of black sheep if
    Peredur uses an optimal strategy.

    You are given that E(5) = 6.871346 rounded to 6 places behind the decimal
    point.
    Find E(10,000) and give your answer rounded to 6 places behind the
    decimal point.

URL: https://projecteuler.net/problem=339
"""
from typing import Any

euler_problem: int = 339
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 20000}, 'answer': None},
]
encrypted: str = (
    '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'
    'oF20UxJG62g+z3izxUwi/PKidOiGyDGC'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
