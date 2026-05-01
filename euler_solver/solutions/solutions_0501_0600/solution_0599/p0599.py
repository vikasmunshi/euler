#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 599: Distinct Colourings of a Rubik's Cube.

Problem Statement:
    The well-known Rubik's Cube puzzle has many fascinating mathematical
    properties. The 2x2x2 variant has 8 cubelets with a total of 24 visible
    faces, each with a coloured sticker. Successively turning faces will
    rearrange the cubelets, although not all arrangements of cubelets are
    reachable without dismantling the puzzle.

    Suppose that we wish to apply new stickers to a 2x2x2 Rubik's cube in a
    non-standard colouring. Specifically, we have n different colours available
    (with an unlimited supply of stickers of each colour), and we place one
    sticker on each of the 24 faces in any arrangement that we please. We are
    not required to use all the colours, and if desired the same colour may
    appear in more than one face of a single cubelet.

    We say that two such colourings c_1, c_2 are essentially distinct if a cube
    coloured according to c_1 cannot be made to match a cube coloured according
    to c_2 by performing mechanically possible Rubik's Cube moves.

    For example, with two colours available, there are 183 essentially distinct
    colourings.

    How many essentially distinct colourings are there with 10 different
    colours available?

URL: https://projecteuler.net/problem=599
"""
from typing import Any

euler_problem: int = 599
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 10}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
