#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 846: Magic Bracelets.

Problem Statement:
    A bracelet is made by connecting at least three numbered beads in a circle.
    Each bead can only display 1, 2, or any number of the form p^k or 2p^k for odd
    prime p.

    In addition a magic bracelet must satisfy the following two conditions:
        no two beads display the same number
        the product of the numbers of any two adjacent beads is of the form x^2+1

    Define the potency of a magic bracelet to be the sum of numbers on its beads.

    The example is a magic bracelet with five beads which has a potency of 155.

    Let F(N) be the sum of the potency of each magic bracelet which can be formed
    using positive integers not exceeding N, where rotations and reflections of an
    arrangement are considered equivalent. You are given F(20)=258 and F(10^2)=538768.

    Find F(10^6).

URL: https://projecteuler.net/problem=846
"""
from typing import Any

euler_problem: int = 846
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 20}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'dAS+0eOepgD3ENLgZvs9pz2AuHbAvqLbpC5PsQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
