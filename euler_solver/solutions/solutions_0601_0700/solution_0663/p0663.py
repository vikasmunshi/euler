#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 663: Sums of Subarrays.

Problem Statement:
    Let t_k be the tribonacci numbers defined as:
        t_0 = t_1 = 0;
        t_2 = 1;
        t_k = t_{k-1} + t_{k-2} + t_{k-3} for k >= 3.

    For a given integer n, let A_n be an array of length n (indexed from 0 to n-1),
    initially filled with zeros.
    The array is changed iteratively by replacing
        A_n[(t_{2i-2} mod n)] with A_n[(t_{2i-2} mod n)] + 2(t_{2i-1} mod n) - n + 1
    at each step i.
    After each step i, define M_n(i) to be max{sum_{j=p}^q A_n[j]: 0 <= p <= q < n},
    the maximal sum of any contiguous subarray of A_n.

    The first 6 steps for n=5 are:
        Initial state: A_5 = {0, 0, 0, 0, 0}
        Step 1: A_5 = {-4, 0, 0, 0, 0}, M_5(1) = 0
        Step 2: A_5 = {-4, -2, 0, 0, 0}, M_5(2) = 0
        Step 3: A_5 = {-4, -2, 4, 0, 0}, M_5(3) = 4
        Step 4: A_5 = {-4, -2, 6, 0, 0}, M_5(4) = 6
        Step 5: A_5 = {-4, -2, 6, 0, 4}, M_5(5) = 10
        Step 6: A_5 = {-4, 2, 6, 0, 4}, M_5(6) = 12

    Let S(n, l) = sum_{i=1}^l M_n(i). Thus S(5,6) = 32.
    Given: S(5,100) = 2416, S(14,100) = 3881, and S(107,1000) = 1618572.

    Find S(10,000,003,10,200,000) - S(10,000,003,10,000,000).

URL: https://projecteuler.net/problem=663
"""
from typing import Any

euler_problem: int = 663
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5, 'l_start': 1, 'l_end': 6}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000003, 'l_start': 10000001, 'l_end': 10200000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
