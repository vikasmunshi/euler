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

Solution Approach:
    Dynamic programming / recursive expectation. Model testing a pooled group of
    k animals: compute probability the pooled test is negative (no further cost)
    and conditioned on positive, the optimal further strategy expected cost.
    Use recurrence T(s,p) = min over partitions/testing choices of expected
    tests; evaluate expected values with binomial probabilities and conditional
    expectations. Key ideas: probability theory, DP with memoization, efficient
    precomputation of binomial tail probabilities (use logs or cumulative DP),
    pruning of search using convexity/monotonicity where applicable. Naive DP is
    O(s^2) per p; optimize to handle s=10000 and many p by reusing computations,
    approximations for large groups, and algorithmic improvements to meet time
    limits.

Answer: ...
URL: https://projecteuler.net/problem=352
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 352
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'s': 25, 'ps': [0.02]}},
    {'category': 'main', 'input': {'s': 10000, 'ps': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.40, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.50]}},
    {'category': 'extra', 'input': {'s': 2000, 'ps': [0.01, 0.02, 0.05, 0.10]}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_blood_tests_p0352_s0(*, s: int, ps: list[float]) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))