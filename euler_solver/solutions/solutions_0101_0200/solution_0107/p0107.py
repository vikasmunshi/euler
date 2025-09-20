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

URL: https://projecteuler.net/problem=107
"""
from typing import Any

euler_problem: int = 107
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'file_url': ''},
     'answer': None},
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0107_network.txt'},
     'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
