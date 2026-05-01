#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 602: Product of Head Counts.

Problem Statement:
    Alice enlists the help of some friends to generate a random number, using a
    single unfair coin. She and her friends sit around a table and, starting with
    Alice, they take it in turns to toss the coin. Everyone keeps a count of how
    many heads they obtain individually. The process ends as soon as Alice obtains
    a Head. At this point, Alice multiplies all her friends' Head counts together
    to obtain her random number.

    As an illustration, suppose Alice is assisted by Bob, Charlie, and Dawn, who
    are seated round the table in that order, and that they obtain the sequence of
    Head/Tail outcomes THHH—TTTT—THHT—H beginning and ending with Alice. Then Bob
    and Charlie each obtain 2 heads, and Dawn obtains 1 head. Alice's random number
    is therefore 2×2×1 = 4.

    Define e(n, p) to be the expected value of Alice's random number, where n is
    the number of friends helping (excluding Alice herself), and p is the
    probability of the coin coming up Tails.

    It turns out that, for any fixed n, e(n, p) is always a polynomial in p. For
    example, e(3, p) = p^3 + 4p^2 + p.

    Define c(n, k) to be the coefficient of p^k in the polynomial e(n, p). So
    c(3, 1) = 1, c(3, 2) = 4, and c(3, 3) = 1.

    You are given that c(100, 40) ≡ 986699437 (mod 10^9+7).

    Find c(10000000, 4000000) mod 10^9+7.

URL: https://projecteuler.net/problem=602
"""
from typing import Any

euler_problem: int = 602
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3, 'k': 2, 'mod': 1000000007}, 'answer': None},
    {'category': 'dev', 'input': {'n': 100, 'k': 40, 'mod': 1000000007}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000, 'k': 4000000, 'mod': 1000000007}, 'answer': None},
]
encrypted: str = (
    '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'
    'tE/EexXh/GSuuHerbcDPtMp51fjmEH0lGlPPpw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
