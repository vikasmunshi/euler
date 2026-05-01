#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 847: Jack's Bean.

Problem Statement:
    Jack has three plates in front of him. The giant has N beans that he distributes
    to the three plates. All the beans look the same, but one of them is a magic
    bean. Jack doesn't know which one it is, but the giant knows.

    Jack can ask the giant questions of the form: "Does this subset of the beans
    contain the magic bean?" In each question Jack may choose any subset of beans
    from a single plate, and the giant will respond truthfully.

    If the three plates contain a, b and c beans respectively, we let h(a, b, c) be
    the minimal number of questions Jack needs to ask in order to guarantee he locates
    the magic bean. For example, h(1, 2, 3) = 3 and h(2, 3, 3) = 4.

    Let H(N) be the sum of h(a, b, c) over all triples of non-negative integers a, b,
    c with 1 ≤ a + b + c ≤ N.
    You are given: H(6) = 203 and H(20) = 7718.

    A repunit, R_n, is a number made up with n digits all '1'. For example, R_3 = 111
    and H(R_3) = 1634144.

    Find H(R_19). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=847
"""
from typing import Any

euler_problem: int = 847
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 6}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1111111111111111111}, 'answer': None},
]
encrypted: str = (
    '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'
    'WjSm6ZakZ6lw6Pf5'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
