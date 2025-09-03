#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 107: Minimal Network.

Problem Statement:
    The following undirected network consists of seven vertices and twelve edges
    with a total weight of 243.

    The same network can be represented by the matrix below.

        A   B   C   D   E   F   G
    A   -  16  12  21   -   -   -
    B  16   -   -  17  20   -   -
    C  12   -   -  28   -  31   -
    D  21  17  28   -  18  19  23
    E   -  20   -  18   -   -  11
    F   -   -  31  19   -   -  27
    G   -   -   -  23  11  27   -

    However, it is possible to optimise the network by removing some edges and
    still ensure that all points on the network remain connected. The network
    which achieves the maximum saving is shown below. It has a weight of 93,
    representing a saving of 243 - 93 = 150 from the original network.

    Using network.txt (right click and 'Save Link/Target As...'), a 6K text file
    containing a network with forty vertices, and given in matrix form, find the
    maximum saving which can be achieved by removing redundant edges whilst
    ensuring that the network remains connected.

Solution Approach:
    Use graph minimum spanning tree concepts. Parse the network matrix from the
    file and compute the sum of all edges. Use algorithms like Kruskal's or
    Prim's to find the MST weight efficiently with union-find or priority queues.
    The answer is total weight minus MST weight (maximum saving). Expected to run
    efficiently for 40 vertices and sparse edges.

Answer: ...
URL: https://projecteuler.net/problem=107
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 107
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'file_url': ''}},
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0107_network.txt'}}
]

example_network: str = ('-, 16, 12, 21, -, -, -\n'
                        '16, -, -, 17, 20, -, -\n'
                        '12, -, -, 28, -, 31, -\n'
                        '21, 17, 28, -, 18, 19, 23\n'
                        '-, 20, -, 18, -, -, 11\n'
                        '-, -, 31, 19, -, -, 27\n'
                        ' -, -, -, 23, 11, 27, -\n')


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_minimal_network_p0107_s0(*, file_url: str) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
