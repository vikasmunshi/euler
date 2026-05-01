#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 314: The Mouse on the Moon.

Problem Statement:
    The moon has been opened up, and land can be obtained for free, but there
    is a catch. You have to build a wall around the land that you stake out,
    and building a wall on the moon is expensive. Every country has been
    allotted a 500 m by 500 m square area, but they will possess only that
    area which they wall in. 251001 posts have been placed in a rectangular
    grid with 1 meter spacing. The wall must be a closed series of straight
    lines, each line running from post to post.
    The bigger countries of course have built a 2000 m wall enclosing the
    entire 250000 m^2 area. The Duchy of Grand Fenwick has a tighter budget,
    and has asked you (their Royal Programmer) to compute what shape would
    give the maximum enclosed-area/wall-length ratio.
    For a 2000 meter wall enclosing the 250000 m^2 area the ratio is 125.
    If you place a circle inside the square touching the four sides the area
    is pi * 250^2 m^2 and the perimeter is pi * 500 m, so the ratio is also
    125. If you cut off from the square four triangles with sides 75 m, 75 m
    and 75*sqrt(2) m the total area becomes 238750 m^2 and the perimeter
    becomes 1400 + 300*sqrt(2) m, giving a ratio of 130.87.
    Find the maximum enclosed-area/wall-length ratio.
    Give your answer rounded to 8 places behind the decimal point in the
    form abc.defghijk.

URL: https://projecteuler.net/problem=314
"""
from typing import Any

euler_problem: int = 314
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'side_m': 10, 'spacing': 1}, 'answer': None},
    {'category': 'main', 'input': {'side_m': 500, 'spacing': 1}, 'answer': None},
    {'category': 'extra', 'input': {'side_m': 1000, 'spacing': 1}, 'answer': None},
]
encrypted: str = (
    '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'
    '026Zk0+7iLdhMgBh'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
