#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 936: Peerless Trees.

Problem Statement:
    A peerless tree is a tree with no edge between two vertices of the same degree.
    Let P(n) be the number of peerless trees on n unlabelled vertices.

    There are six of these trees on seven unlabelled vertices, P(7) = 6.

    Define S(N) = sum of P(n) for n = 3 to N. You are given S(10) = 74.

    Find S(50).

URL: https://projecteuler.net/problem=936
"""
from typing import Any

euler_problem: int = 936
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 50}, 'answer': None},
]
encrypted: str = (
    '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'
    'yhp8pWDJrgMbNssfoTfxEldqoh4='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
