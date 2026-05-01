#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 352: Blood Tests.

Problem Statement:
    Each one of the 25 sheep in a flock must be tested for a rare virus, known to
    affect 2% of the sheep population. An accurate PCR test exists producing a
    clear positive / negative result, but it is time-consuming and expensive.

    Instead of performing 25 separate tests, samples may be mixed and tested in
    groups. One scheme: split into 5 groups of 5, test each pooled sample once;
    if the pooled result is negative all 5 are deemed virus-free; if positive,
    test each individual in that group. For p = 0.02 the pooled test for 5 is
    negative with probability 0.98^5 = 0.9039207968, positive with probability
    0.0960792032, so expected tests per group = 1 + 0.0960792032*5 = 1.480396016,
    and for 5 groups the expected total is 7.40198008.

    Better strategies exist: e.g., start by testing all 25 together, which is
    negative about 60.35% of the time; if a pooled test is positive one may
    adaptively test subsets or individuals and stop testing particular animals
    when their status becomes certain. A restriction: whenever we start with a
    mixed sample, all sheep contributing to that sample must be fully screened
    before any other animals are examined.

    Define T(s,p) as the average number of tests needed to screen s sheep where
    each animal has independent infection probability p. For example,
    T(25, 0.02) = 4.155452 (rounded to six decimals) and
    T(25, 0.10) = 12.702124.

    Find sum_{p=0.01,0.02,...,0.50} T(10000, p). Give the answer rounded to six
    decimal places.

URL: https://projecteuler.net/problem=352
"""
from typing import Any

euler_problem: int = 352
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'s': 25, 'ps': [0.02]},
     'answer': None},
    {'category': 'main', 'input': {'s': 10000, 'ps': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11,
                                                      0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.21, 0.22,
                                                      0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33,
                                                      0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.4, 0.41, 0.42, 0.43, 0.44,
                                                      0.45, 0.46, 0.47, 0.48, 0.49, 0.5]},
     'answer': None},
    {'category': 'extra', 'input': {'s': 2000, 'ps': [0.01, 0.02, 0.05, 0.1]},
     'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
