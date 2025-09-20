#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 857: Beautiful Graphs.

Problem Statement:
    A graph is made up of vertices and coloured edges.
    Between every two distinct vertices there must be exactly one of the following:
        - A red directed edge one way, and a blue directed edge the other way
        - A green undirected edge
        - A brown undirected edge

    Such a graph is called beautiful if:
        - A cycle of edges contains a red edge if and only if it also contains a blue edge
        - No triangle of edges is made up of entirely green or entirely brown edges

    Four distinct examples of beautiful graphs on three vertices are shown (not included here).
    Also, four examples of graphs that are not beautiful are shown (not included here).

    Let G(n) be the number of beautiful graphs on the labelled vertices: 1,2,...,n.
    Given G(3)=24, G(4)=186, and G(15)=12472315010483328.

    Find G(10^7). Give your answer modulo 10^9+7.

URL: https://projecteuler.net/problem=857
"""
from typing import Any

euler_problem: int = 857
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
