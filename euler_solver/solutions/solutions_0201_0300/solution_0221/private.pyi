#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 221: Alexandrian Integers.

Problem Statement:
    We shall call a positive integer A an "Alexandrian integer", if there exist
    integers p, q, r such that:

    A = p * q * r
    and
    1/A = 1/p + 1/q + 1/r.

    For example, 630 is an Alexandrian integer (p = 5, q = -7, r = -18).
    In fact, 630 is the 6th Alexandrian integer, the first 6 being:
    6, 42, 120, 156, 420, 630.

    Find the 150000th Alexandrian integer.

Solution Approach:
    Use the diophantine relation pq + pr + qr = 1 derived from 1/A = 1/p+1/q+1/r.
    Parameterize candidate integer triples (p, q, r) by iterating integer pairs
    and checking the resulting divisibility condition for the third value.
    For each valid triple compute A = p*q*r, keep distinct positive A values,
    and extract them in ascending order (min-heap or sort) until the nth is found.
    Use bounding and pruning to avoid unnecessary pairs; target O(n log n) time.

Answer: ...
URL: https://projecteuler.net/problem=221
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 221
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 6}},
    {'category': 'main', 'input': {'n': 150000}},
    {'category': 'extra', 'input': {'n': 100000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_alexandrian_integers_p0221_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))