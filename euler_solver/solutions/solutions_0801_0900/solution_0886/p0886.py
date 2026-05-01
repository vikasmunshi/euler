#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 886: Coprime Permutations.

Problem Statement:
    A permutation of {2,3,...,n} is a rearrangement of these numbers. A coprime
    permutation is a rearrangement such that all pairs of adjacent numbers are
    coprime.

    Let P(n) be the number of coprime permutations of {2,3,...,n}.

    For example, P(4)=2 as there are two coprime permutations, (2,3,4) and (4,3,2).
    You are also given P(10)=576.

    Find P(34) and give your answer modulo 83456729.

URL: https://projecteuler.net/problem=886
"""
from typing import Any

euler_problem: int = 886
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
