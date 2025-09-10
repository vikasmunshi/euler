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

Solution Approach:
    Model the generation of b(n) by a small finite automaton tracking the last
    bit and whether an adjacent-one was just formed; use digit-DP over binary
    prefixes to count contributions to s(n) up to any bound x.
    For a given target t and occurrence c, use binary search on x while using
    the DP to count how many indices n <= x produce s(n) < t and how many
    equal t, thereby locating g(t,c). Compute GF(t) with F(t),F(t-1) and sum.
    Key ideas: automaton/digit-DP on binary digits, binary search, prefix
    counting. Expected complexity: poly(bits, states) per query; overall
    about O(T * states * bits * log X) where T=number of t values.

Answer: ...
URL: https://projecteuler.net/problem=384
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 384
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'t_max': 6}},
    {'category': 'main', 'input': {'t_max': 45}},
    {'category': 'extra', 'input': {'t_max': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_rudin_shapiro_sequence_p0384_s0(*, t_max: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))