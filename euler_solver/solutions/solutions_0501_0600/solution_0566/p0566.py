#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 566: Cake Icing Puzzle.

Problem Statement:
    Adam plays the following game with his birthday cake.

    He cuts a piece forming a circular sector of 60 degrees and flips the piece
    upside down, with the icing on the bottom.
    He then rotates the cake by 60 degrees counterclockwise, cuts an adjacent
    60 degree piece and flips it upside down.
    He keeps repeating this, until after a total of twelve steps, all the icing
    is back on top.

    Amazingly, this works for any piece size, even if the cutting angle is an
    irrational number: all the icing will be back on top after a finite number
    of steps.

    Now, Adam tries something different: he alternates cutting pieces of size
    x = 360/9 degrees, y = 360/10 degrees and z = 360/sqrt(11) degrees. The
    first piece he cuts has size x and he flips it. The second has size y and
    he flips it. The third has size z and he flips it. He repeats this with
    pieces of size x, y and z in that order until all the icing is back on top,
    and discovers he needs 60 flips altogether.

    Let F(a, b, c) be the minimum number of piece flips needed to get all the
    icing back on top for pieces of size x = 360/a degrees, y = 360/b degrees
    and z = 360/sqrt(c) degrees.
    Let G(n) = sum_{9 <= a < b < c <= n} F(a,b,c), for integers a, b and c.

    You are given that F(9, 10, 11) = 60, F(10, 14, 16) = 506, F(15, 16, 17) = 785232.
    You are also given G(11) = 60, G(14) = 58020 and G(17) = 1269260.

    Find G(53).

URL: https://projecteuler.net/problem=566
"""
from typing import Any

euler_problem: int = 566
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 11}, 'answer': None},
    {'category': 'main', 'input': {'n': 53}, 'answer': None},
]
encrypted: str = (
    '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'
    'FUdFRPCF+DjNP/NNB5PqKfZPdxgtyDW/hwpYRg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
