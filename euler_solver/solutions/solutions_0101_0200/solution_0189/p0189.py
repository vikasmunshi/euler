#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 189: Tri-colouring a Triangular Grid.

Problem Statement:
    Consider the following configuration of 64 triangles:
    (triangular grid diagram)

    We wish to colour the interior of each triangle with one of three colours:
    red, green or blue, so that no two neighbouring triangles have the same
    colour. Two triangles are neighbouring if they share an edge; sharing a
    vertex does not make them neighbours.

    For example, a valid colouring of the above grid is shown.

    A colouring C' which is obtained from a colouring C by rotation or
    reflection is considered distinct from C unless the two are identical.

    How many distinct valid colourings are there for the above configuration?

URL: https://projecteuler.net/problem=189
"""
from typing import Any

euler_problem: int = 189
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'fUQnfIdbPjd60vfT'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
