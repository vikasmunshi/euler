#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 762: Amoebas in a 2D Grid.

Problem Statement:
    Consider a two dimensional grid of squares. The grid has 4 rows but infinitely many
    columns.

    An amoeba in square (x, y) can divide itself into two amoebas to occupy the squares
    (x+1, y) and (x+1, (y+1) mod 4), provided these squares are empty.

    The following diagrams show two cases of an amoeba placed in square A of each grid.
    When it divides, it is replaced with two amoebas, one at each of the squares marked
    with B.

    Originally there is only one amoeba in the square (0, 0). After N divisions there will
    be N+1 amoebas arranged in the grid. An arrangement may be reached in several
    different ways but it is only counted once. Let C(N) be the number of different
    possible arrangements after N divisions.

    For example, C(2) = 2, C(10) = 1301, C(20) = 5895236 and the last nine digits of
    C(100) are 125923036.

    Find C(100000), enter the last nine digits as your answer.

URL: https://projecteuler.net/problem=762
"""
from typing import Any

euler_problem: int = 762
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'divisions': 100000}, 'answer': None},
]
encrypted: str = (
    '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'
    'P6QWO7ND35O5CbCoVKEUU2r9WIyuZPLM'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
