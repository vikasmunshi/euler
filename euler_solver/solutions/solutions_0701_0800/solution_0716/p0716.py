#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 716: Grid Graphs.

Problem Statement:
    Consider a directed graph made from an orthogonal lattice of H times W nodes.
    The edges are the horizontal and vertical connections between adjacent nodes.
    W vertical directed lines are drawn and all the edges on these lines inherit that
    direction. Similarly, H horizontal directed lines are drawn and all the edges on
    these lines inherit that direction.

    Two nodes, A and B in a directed graph, are strongly connected if there is both a
    path, along the directed edges, from A to B as well as from B to A. Note that every
    node is strongly connected to itself.

    A strongly connected component in a directed graph is a non-empty set M of nodes
    satisfying the following two properties:
        - All nodes in M are strongly connected to each other.
        - M is maximal, in the sense that no node in M is strongly connected to any node
          outside of M.

    There are 2^H times 2^W ways of drawing the directed lines. Each way gives a directed
    graph G. We define S(G) to be the number of strongly connected components in G.

    The illustration below shows a directed graph with H=3 and W=4 that consists of four
    different strongly connected components (indicated by the different colours).

    Define C(H,W) to be the sum of S(G) for all possible graphs on a grid of H times W.
    You are given C(3,3) = 408, C(3,6) = 4696 and C(10,20) congruent to 988971143 modulo
    1000000007.

    Find C(10000,20000) giving your answer modulo 1000000007.

URL: https://projecteuler.net/problem=716
"""
from typing import Any

euler_problem: int = 716
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'H': 3, 'W': 3}, 'answer': None},
    {'category': 'main', 'input': {'H': 10000, 'W': 20000}, 'answer': None},
    {'category': 'extra', 'input': {'H': 50, 'W': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
