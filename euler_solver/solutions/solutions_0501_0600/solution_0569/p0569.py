#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 569: Prime Mountain Range.

Problem Statement:
    A mountain range consists of a line of mountains with slopes of exactly 45 degrees,
    and heights governed by the prime numbers, p_n. The up-slope of the k-th mountain
    is of height p_(2k - 1), and the downslope is p_(2k). The first few foot-hills of
    this range are illustrated.

    Tenzing sets out to climb each one in turn, starting from the lowest. At the top
    of each peak, he looks back and counts how many of the previous peaks he can see.
    For example, from the third mountain he can see only the peak of the second mountain.
    From the 9th mountain, he can see three peaks, those of the 5th, 7th, and 8th mountain.

    Let P(k) be the number of peaks that are visible looking back from the k-th mountain.
    Hence P(3)=1 and P(9)=3.
    Also the sum from k=1 to 100 of P(k) is 227.

    Find the sum from k=1 to 2500000 of P(k).

URL: https://projecteuler.net/problem=569
"""
from typing import Any

euler_problem: int = 569
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 2500000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
