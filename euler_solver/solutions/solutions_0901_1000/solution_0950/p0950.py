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

URL: https://projecteuler.net/problem=950
"""
from typing import Any

euler_problem: int = 950
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 5, 'C': 5, 'p': 0.1}, 'answer': None},
    {'category': 'main', 'input': {'N': 10000000000000000, 'C': 2, 'p': 0.707106781373095}, 'answer': None},
]
encrypted: str = (
    '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'
    'JBeal39fc38='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
