#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 116: Red, Green or Blue Tiles.

Problem Statement:
    A row of five grey square tiles is to have a number of its tiles replaced
    with coloured oblong tiles chosen from red (length two), green (length three),
    or blue (length four).

    If red tiles are chosen there are exactly seven ways this can be done.

    If green tiles are chosen there are three ways.

    And if blue tiles are chosen there are two ways.

    Assuming that colours cannot be mixed there are 7 + 3 + 2 = 12 ways of
    replacing the grey tiles in a row measuring five units in length.

    How many different ways can the grey tiles in a row measuring fifty units in
    length be replaced if colours cannot be mixed and at least one coloured tile
    must be used?

URL: https://projecteuler.net/problem=116
"""
from typing import Any

euler_problem: int = 116
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'row_length': 5}, 'answer': None},
    {'category': 'main', 'input': {'row_length': 50}, 'answer': None},
]
encrypted: str = (
    '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'
    '50w/AvSbM3BgTok0/v744A=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
