#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 267: Billionaire.

Problem Statement:
    You are given a unique investment opportunity.
    Starting with £1 of capital, you can choose a fixed proportion, f, of your
    capital to bet on a fair coin toss repeatedly for 1000 tosses.
    Your return is double your bet for heads and you lose your bet for tails.
    For example, if f = 1/4, for the first toss you bet £0.25, and if heads
    comes up you win £0.5 and so then have £1.5. You then bet £0.375 and if
    the second toss is tails, you have £1.125.
    Choosing f to maximize your chances of having at least £1,000,000,000
    after 1,000 flips, what is the chance that you become a billionaire?
    All computations are assumed to be exact (no rounding), but give your
    answer rounded to 12 digits behind the decimal point in the form
    0.abcdefghijkl.

Solution Approach:
    Model wealth after n tosses: for k heads W = (1+f)^k * (1-f)^(n-k), start at 1.
    For fixed f, find minimal k threshold so W >= target, then probability is
    sum_{k>=k_min} C(n,k) / 2^n (binomial tail). Use log transforms to avoid
    underflow: compare k*log(1+f) + (n-k)*log(1-f) to log(target).
    Optimize over f in (0,1) to maximize the binomial tail probability. Key
    techniques: probability (binomial tails), numerical optimization (unimodal
    search), approximations (normal or saddle-point for tails) and high-prec
    logs. Expect O(n) or O(n log n) per f-evaluation; overall cost depends on
    optimization iterations. Use careful numerical stability and cumulative
    binomial evaluation or normal approximation to meet precision.

Answer: ...
URL: https://projecteuler.net/problem=267
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 267
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_flips': 10, 'target': 1000}},
    {'category': 'main', 'input': {'num_flips': 1000, 'target': 1000000000}},
    {'category': 'extra', 'input': {'num_flips': 2000, 'target': 1000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_billionaire_p0267_s0(*, num_flips: int, target: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))