#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 732: Standing on the Shoulders of Trolls.

Problem Statement:
    N trolls are in a hole that is D_N cm deep. The n-th troll is characterized by:
        - the distance from his feet to his shoulders in cm, h_n
        - the length of his arms in cm, l_n
        - his IQ (Irascibility Quotient), q_n.

    Trolls can pile up on top of each other, with each troll standing on the shoulders
    of the one below him. A troll can climb out of the hole and escape if his hands
    can reach the surface. Once a troll escapes he cannot participate any further in
    the escaping effort.

    The trolls execute an optimal strategy for maximizing the total IQ of the escaping
    trolls, defined as Q(N).

    Let
        r_n = [ (5^n mod (10^9 + 7)) mod 101 ] + 50
        h_n = r_(3n)
        l_n = r_(3n+1)
        q_n = r_(3n+2)
        D_N = (1 / sqrt(2)) * sum_{n=0}^{N-1} h_n.

    For example, the first troll (n=0) is 51cm tall to his shoulders, has 55cm long arms,
    and has an IQ of 75.

    You are given that Q(5) = 401 and Q(15) = 941.

    Find Q(1000).

URL: https://projecteuler.net/problem=732
"""
from typing import Any

euler_problem: int = 732
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1500}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
