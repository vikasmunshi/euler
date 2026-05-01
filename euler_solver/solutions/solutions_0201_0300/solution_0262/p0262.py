#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 262: Mountain Range.

Problem Statement:
    The continuous topography of a region gives elevation h at any point (x, y):
    h = (5000 - (x^2 + y^2 + x*y)/200 + 25*(x + y)/2)
        * exp( -| (x^2 + y^2)/1000000 - 3*(x + y)/2000 + 7/10 | ).

    A mosquito flies from A(200,200) to B(1400,1400) while staying within
    0 <= x, y <= 1600. It first rises vertically to elevation f at A',
    then, remaining exactly at elevation f, flies around obstacles until it
    reaches B' above B.

    Determine f_min, the minimum constant elevation that allows such a
    trip (so the horizontal path at z = f_min does not intersect terrain),
    then find the length of the shortest horizontal path between A' and B'
    at that elevation. Give the length rounded to three decimal places.

    Programming form of the height function (for reference):
    h = ( 5000-0.005*(x*x+y*y+x*y)+12.5*(x+y) ) \
        * exp( -abs(0.000001*(x*x+y*y)-0.0015*(x+y)+0.7) )

URL: https://projecteuler.net/problem=262
"""
from typing import Any

euler_problem: int = 262
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'O/Sy9o8aYGI='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
