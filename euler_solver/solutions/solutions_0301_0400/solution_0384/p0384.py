#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 384: Rudin-Shapiro Sequence.

Problem Statement:
    Define the sequence a(n) as the number of adjacent pairs of ones in the
    binary expansion of n (possibly overlapping).
    E.g.: a(5) = a(101_2) = 0, a(6) = a(110_2) = 1, a(7) = a(111_2) = 2.
    Define the sequence b(n) = (-1)^{a(n)}. This sequence is the Rudin-Shapiro
    sequence. Also consider the summatory sequence s(n) = sum_{i=0}^n b(i).
    The first values are:
        n:  0 1 2 3 4 5 6 7
        a:  0 0 0 1 0 0 1 2
        b:  1 1 1 -1 1 1 -1 1
        s:  1 2 3 2 3 4 3 4
    The sequence s(n) has the property that all elements are positive and every
    positive integer k occurs exactly k times.
    Define g(t,c) with 1 <= c <= t as the index n for which t occurs for the
    c'th time in s(n). E.g.: g(3,3) = 6, g(4,2) = 7 and
    g(54321,12345) = 1220847710.
    Let F(n) be the Fibonacci sequence with F(0)=F(1)=1 and F(n)=F(n-1)+F(n-2)
    for n > 1. Define GF(t) = g(F(t),F(t-1)). Find sum GF(t) for 2 <= t <= 45.

URL: https://projecteuler.net/problem=384
"""
from typing import Any

euler_problem: int = 384
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'t_max': 6}, 'answer': None},
    {'category': 'main', 'input': {'t_max': 45}, 'answer': None},
    {'category': 'extra', 'input': {'t_max': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
