#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 781: Feynman Diagrams.

Problem Statement:
    Let F(n) be the number of connected graphs with blue edges (directed) and red edges
    (undirected) containing:
        two vertices of degree 1, one with a single outgoing blue edge and the other with a
        single incoming blue edge.
        n vertices of degree 3, each of which has an incoming blue edge, a different outgoing
        blue edge and a red edge.

    For example, F(4) = 5 because there are 5 graphs with these properties.

    You are also given F(8) = 319.

    Find F(50000). Give your answer modulo 1000000007.

    NOTE: Feynman diagrams are a way of visualising the forces between elementary particles.
    Vertices represent interactions. The blue edges in our diagrams represent matter particles
    (e.g. electrons or positrons) with the arrow representing the flow of charge. The red
    edges (normally wavy lines) represent the force particles (e.g. photons). Feynman diagrams
    are used to predict the strength of particle interactions.

URL: https://projecteuler.net/problem=781
"""
from typing import Any

euler_problem: int = 781
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 50000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
