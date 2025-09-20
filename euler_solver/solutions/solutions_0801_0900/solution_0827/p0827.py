#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 827: Pythagorean Triple Occurrence.

Problem Statement:
    Define Q(n) to be the smallest number that occurs in exactly n Pythagorean triples
    (a,b,c) where a < b < c.

    For example, 15 is the smallest number occurring in exactly 5 Pythagorean triples:
    (9,12,15) (8,15,17) (15,20,25) (15,36,39) (15,112,113)
    and so Q(5) = 15.

    You are also given Q(10) = 48 and Q(10^3) = 8064000.

    Find the sum from k=1 to 18 of Q(10^k). Give your answer modulo 409120391.

URL: https://projecteuler.net/problem=827
"""
from typing import Any

euler_problem: int = 827
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
