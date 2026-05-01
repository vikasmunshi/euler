#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 943: Self Describing Sequences.

Problem Statement:
    Given two unequal positive integers a and b, we define a self-describing
    sequence consisting of alternating runs of a's and b's. The first element
    is a and the sequence of run lengths is the original sequence.

    For a=2, b=3, the sequence is:
    2, 2, 3, 3, 2, 2, 2, 3, 3, 3, 2, 2, 3, 3, 2, 2, 3, 3, 3, 2, 2, 2, 3, 3, 3,...
    The sequence begins with two 2s and two 3s, then three 2s and three 3s, so the
    run lengths 2, 2, 3, 3, ... are given by the original sequence.

    Let T(a, b, N) be the sum of the first N elements of the sequence. You are given:
    T(2,3,10) = 25, T(4,2,10^4) = 30004, T(5,8,10^6) = 6499871.

    Find the sum of T(a, b, 22332223332233) for 2 <= a <= 223, 2 <= b <= 223 and a ≠ b.
    Give your answer modulo 2233222333.

URL: https://projecteuler.net/problem=943
"""
from typing import Any

euler_problem: int = 943
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'a_min': 2, 'a_max': 223,
                                   'b_min': 2, 'b_max': 223,
                                   'N': 22332223332233, 'modulus': 2233222333},
     'answer': None},
]
encrypted: str = (
    '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'
    'wgVfdmuaRn5Yi1LREFt4Up62cJNgzKixSiixoA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
