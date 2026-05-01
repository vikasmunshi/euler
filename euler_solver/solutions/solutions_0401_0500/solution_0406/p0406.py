#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 406: Guessing Game.

Problem Statement:
    We are trying to find a hidden number selected from the set of integers {1, 2, ..., n}
    by asking questions. Each number (question) we ask, we get one of three possible answers:
        "Your guess is lower than the hidden number" (cost a),
        "Your guess is higher than the hidden number" (cost b),
        or "Yes, that's it!" (game ends).
    An optimal strategy minimizes the total cost for the worst possible case.

    Example: if n=5, a=2, b=3, one optimal strategy is:
        Ask "2" first.
        If told "higher" (cost 3), answer is 1 (total cost 3).
        If told "lower" (cost 2), next ask "4":
            If "higher" (cost 3), answer is 3 (cost 5 total).
            If "lower" (cost 2), answer is 5 (cost 4 total).
    Worst-case cost with this strategy is 5, which is minimal.

    Define C(n,a,b) as the worst-case cost of an optimal strategy for given n,a,b.

    Examples:
        C(5, 2, 3) = 5
        C(500, sqrt(2), sqrt(3)) = 13.22073197...
        C(20000, 5, 7) = 82
        C(2000000, sqrt(5), sqrt(7)) = 49.63755955...

    Let F_k be Fibonacci numbers: F_1=1, F_2=1, F_k=F_{k-1}+F_{k-2}.

    Find the sum from k=1 to 30 of C(10^12, sqrt(k), sqrt(F_k)) rounded to 8 decimals.

URL: https://projecteuler.net/problem=406
"""
from typing import Any

euler_problem: int = 406
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 1000000000000, 'k': 30}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
