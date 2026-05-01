#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 756: Approximating a Sum.

Problem Statement:
    Consider a function f(k) defined for all positive integers k>0. Let S be the sum
    of the first n values of f. That is,
    S = f(1) + f(2) + f(3) + ... + f(n) = sum_{k=1}^n f(k).

    In this problem, we employ randomness to approximate this sum. That is, we choose a
    random, uniformly distributed, m-tuple of positive integers (X_1,X_2,...,X_m) such that
    0 = X_0 < X_1 < X_2 < ... < X_m <= n and calculate a modified sum S* as follows.
    S* = sum_{i=1}^m f(X_i) * (X_i - X_{i-1})

    We now define the error of this approximation to be Δ = S - S*.

    Let E(Δ | f(k), n, m) be the expected value of the error given the function f(k),
    the number of terms n in the sum and the length of random sample m.

    For example, E(Δ | k, 100, 50) = 2525/1326 ≈ 1.904223 and
    E(Δ | φ(k), 10^4, 10^2) ≈ 5842.849907, where φ(k) is Euler's totient function.

    Find E(Δ | φ(k), 12345678, 12345) rounded to six places after the decimal point.

URL: https://projecteuler.net/problem=756
"""
from typing import Any

euler_problem: int = 756
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 100, 'm': 50}, 'answer': None},
    {'category': 'main', 'input': {'n': 12345678, 'm': 12345}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
