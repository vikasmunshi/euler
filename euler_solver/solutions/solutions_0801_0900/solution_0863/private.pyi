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

Solution Approach:
    Use probability and Markov process modeling of predetermined dice roll sequences.
    Calculate expected rolls by solving linear systems for each n using dynamic programming
    and state transitions with modular arithmetic.
    Number theory and discrete distributions to optimize for minimal expected rolls.
    Efficient iterative or matrix-based numerical methods for large n.
    Time complexity expected to be polynomial with careful pruning, space also polynomial.

Answer: ...
URL: https://projecteuler.net/problem=863
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 863
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 30}},
    {'category': 'main', 'input': {'max_n': 1000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_different_dice_p0863_s0(*, max_n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))