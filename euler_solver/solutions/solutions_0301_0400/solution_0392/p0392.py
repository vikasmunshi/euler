#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 392: Enmeshed Unit Circle.

Problem Statement:
    A rectilinear grid is an orthogonal grid where the spacing between the grid
    lines does not have to be equidistant. An example is logarithmic graph paper.
    Consider rectilinear grids in the Cartesian coordinate system with the
    following properties:
    - The gridlines are parallel to the axes of the Cartesian coordinate system.
    - There are N+2 vertical and N+2 horizontal gridlines. Hence there are
      (N+1) x (N+1) rectangular cells.
    - The equations of the two outer vertical gridlines are x = -1 and x = 1.
    - The equations of the two outer horizontal gridlines are y = -1 and y = 1.
    - The grid cells are colored red if they overlap with the unit circle,
      black otherwise.
    We want to find positions of the remaining N inner horizontal and N inner
    vertical gridlines so that the total area occupied by the red cells is
    minimized.
    For example, for N = 10 the area occupied by red cells rounded to 10
    digits is 3.3469640797.
    Find the positions for N = 400 and give the area occupied by the red cells
    rounded to 10 digits behind the decimal point.

URL: https://projecteuler.net/problem=392
"""
from typing import Any

euler_problem: int = 392
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 10}, 'answer': None},
    {'category': 'main', 'input': {'N': 400}, 'answer': None},
]
encrypted: str = (
    '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'
    'AW+wzfVejkrgtSdQ046uvd13Gg0zP/dM'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
