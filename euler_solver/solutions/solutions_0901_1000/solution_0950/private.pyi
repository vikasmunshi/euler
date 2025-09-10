#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 950: Pirate Treasure.

Problem Statement:
    A band of pirates has come into a hoard of treasure, and must decide how to
    distribute it amongst themselves. The treasure consists of identical, indivisible
    gold coins.

    According to pirate law, the distribution of treasure must proceed as follows:
        1. The most senior pirate proposes a distribution of the coins.
        2. All pirates, including the most senior, vote on whether to accept the
           distribution.
        3. If at least half of the pirates vote to accept, the distribution stands.
        4. Otherwise, the most senior pirate must walk the plank, and the process
           resumes from step 1 with the next most senior pirate proposing another
           distribution.

    The happiness of a pirate is equal to -∞ if he doesn't survive; otherwise, it is
    equal to c + p·w, where c is the number of coins that pirate receives in the
    distribution, w is the total number of pirates who were made to walk the plank,
    and p is the bloodthirstiness of the pirate.

    The pirates have a number of characteristics:
        • Greed: to maximise their happiness.
        • Ruthlessness: incapable of cooperation, making promises or maintaining any
          kind of reputation.
        • Shrewdness: perfectly rational and logical.

    Consider the happiness c(n,C,p) + p·w(n,C,p) of the most senior surviving pirate
    in the situation where n pirates, all with equal bloodthirstiness p, have found C
    coins. For example, c(5,5,1/10) = 3 and w(5,5,1/10) = 0 because it can be shown that
    if the most senior pirate proposes a distribution of 3,0,1,0,1 coins to the pirates
    (in decreasing order of seniority), the three pirates receiving coins will all vote
    to accept. On the other hand, c(5,1,1/10) = 0 and w(5,1,1/10) = 1: the most senior
    pirate cannot survive with any proposal, and then the second most senior pirate must
    give the only coin to another pirate in order to survive.

    Define T(N,C,p) = ∑_{n=1}^N (c(n,C,p) + w(n,C,p)). You are given that
    T(30,3,1/√3) = 190, T(50,3,1/√31) = 385, and T(10^3,101,1/√101) = 142427.

    Find ∑_{k=1}^6 T(10^16,10^k+1,1/√(10^k+1)). Give the last 9 digits as your answer.

Solution Approach:
    Model the pirates' decision and distribution process using game theory and
    combinatorics, focusing on their rationality and voting behavior.
    Calculate the most senior pirate’s happiness and the plank-walk count recursively
    or via dynamic programming.
    Exploit symmetry due to equal bloodthirstiness and optimize through mathematical
    identities or properties.
    Handle extremely large inputs (up to 10^16 pirates) with formulas or analytical
    simplifications, avoiding direct simulation.
    Use modular arithmetic for large sums to get last 9 digits efficiently.
    Complexity reduction via insight into pirates' voting thresholds and survival rules.

Answer: ...
URL: https://projecteuler.net/problem=950
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 950
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 5, 'C': 5, 'p': 1/10}},
    {'category': 'main', 'input': {'N': 10**16, 'C': 2, 'p': 1/1.414213562}},  # p ≈ 1/sqrt(2) for a simpler C for prelim main example
]

@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_pirate_treasure_p0950_s0(*, N: int, C: int, p: float) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))