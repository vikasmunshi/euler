#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 906: A Collective Decision.

Problem Statement:
    Three friends attempt to collectively choose one of n options, labeled 1,...,n,
    based upon their individual preferences. They choose option i if for every
    alternative option j at least two of the three friends prefer i over j. If
    no such option i exists they fail to reach an agreement.

    Define P(n) to be the probability the three friends successfully reach an agreement
    and choose one option, where each of the friends' individual order of preference
    is given by a (possibly different) random permutation of 1,...,n.

    You are given P(3)=17/18 and P(10)≈0.6760292265.

    Find P(20,000). Give your answer rounded to ten places after the decimal point.

URL: https://projecteuler.net/problem=906
"""
from typing import Any

euler_problem: int = 906
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 20000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
