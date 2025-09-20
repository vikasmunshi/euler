#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 746: A Messy Dinner.

Problem Statement:
    n families, each with four members, a father, a mother, a son and a daughter,
    were invited to a restaurant. They were all seated at a large circular table
    with 4n seats such that men and women alternate.

    Let M(n) be the number of ways the families can be seated such that none of
    the families were seated together. A family is considered to be seated
    together only when all the members of a family sit next to each other.

    For example, M(1)=0, M(2)=896, M(3)=890880 and M(10) ≡ 170717180 mod 1,000,000,007.

    Let S(n) = sum from k=2 to n of M(k).

    For example, S(10) ≡ 399291975 mod 1,000,000,007.

    Find S(2021). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=746
"""
from typing import Any

euler_problem: int = 746
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 3}, 'answer': None},
    {'category': 'main', 'input': {'max_n': 2021}, 'answer': None},
]
encrypted: str = (
    '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'
    'm9iVLpTiR78='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
