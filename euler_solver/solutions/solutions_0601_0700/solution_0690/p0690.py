#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 690: Tom and Jerry.

Problem Statement:
    Tom (the cat) and Jerry (the mouse) are playing on a simple graph G.
    Every vertex of G is a mousehole, and every edge of G is a tunnel
    connecting two mouseholes.

    Originally, Jerry is hiding in one of the mouseholes.
    Every morning, Tom can check one (and only one) of the mouseholes. If
    Jerry happens to be hiding there then Tom catches Jerry and the game
    is over.
    Every evening, if the game continues, Jerry moves to a mousehole which
    is adjacent (i.e. connected by a tunnel, if there is one available)
    to his current hiding place. The next morning Tom checks again and
    the game continues like this.

    Let us call a graph G a Tom graph, if our super-smart Tom, who knows
    the configuration of the graph but does not know the location of Jerry,
    can guarantee to catch Jerry in finitely many days.
    For example consider all graphs on 3 nodes:

    For graphs 1 and 2, Tom will catch Jerry in at most three days. For
    graph 3 Tom can check the middle connection on two consecutive days
    and hence guarantee to catch Jerry in at most two days. These three
    graphs are therefore Tom Graphs. However, graph 4 is not a Tom Graph
    because the game could potentially continue forever.

    Let T(n) be the number of different Tom graphs with n vertices. Two
    graphs are considered the same if there is a bijection f between their
    vertices, such that (v,w) is an edge if and only if (f(v),f(w)) is an
    edge.

    We have T(3) = 3, T(7) = 37, T(10) = 328 and T(20) = 1416269.

    Find T(2019) giving your answer modulo 1000000007.

URL: https://projecteuler.net/problem=690
"""
from typing import Any

euler_problem: int = 690
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
