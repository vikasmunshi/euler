#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 863: Different Dice.

Problem Statement:
    Using only a six-sided fair dice and a five-sided fair dice, we would like to
    emulate an n-sided fair dice.

    For example, one way to emulate a 28-sided dice is to follow this procedure:

        1. Roll both dice, obtaining integers 1 ≤ p ≤ 6 and 1 ≤ q ≤ 5.
        2. Combine them using r = 5(p-1) + q to obtain an integer 1 ≤ r ≤ 30.
        3. If r ≤ 28, return the value r and stop.
        4. Otherwise (r being 29 or 30), roll both dice again, obtaining integers
           1 ≤ s ≤ 6 and 1 ≤ t ≤ 5.
        5. Compute u = 30(r-29) + 5(s-1) + t to obtain 1 ≤ u ≤ 60.
        6. If u > 4, return ((u-5) mod 28) + 1 and stop.
        7. Otherwise (1 ≤ u ≤ 4), roll the six-sided dice twice, obtaining integers
           1 ≤ v, w ≤ 6.
        8. Compute x = 36(u-1) + 6(v-1) + w to obtain 1 ≤ x ≤ 144.
        9. If x > 4, return ((x-5) mod 28) + 1 and stop.
        10. Otherwise (1 ≤ x ≤ 4), assign u := x and go back to step 7.

    The expected number of dice rolls in this procedure is 2.142476 (rounded to 6 decimals).
    Rolling both dice simultaneously counts as two dice rolls.

    Other procedures for emulating a 28-sided dice may yield a smaller average number of
    rolls, but this procedure has the predetermined sequence (D5, D6, D5, D6, D6, D6, D6, ...)
    truncated where the process stops. Among procedures with this restriction, it is optimal
    minimizing the expected rolls.

    Different n will use different predetermined sequences. For example, for n=8, the sequence
    (D5, D5, D5, ...) is optimal with expected rolls 2.083333...

    Define R(n) as the expected rolls for an optimal predetermined sequence procedure emulating
    an n-sided dice with only a 5-sided and a 6-sided dice. R(8)≈2.083333 and R(28)≈2.142476.

    Let S(n) = sum of R(k) for k=2 to n. It is given that S(30) ≈ 56.054622.

    Find S(1000), rounded to 6 decimal places.

URL: https://projecteuler.net/problem=863
"""
from typing import Any

euler_problem: int = 863
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 30}, 'answer': None},
    {'category': 'main', 'input': {'max_n': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
    '9/BYYQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
