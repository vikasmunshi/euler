#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 329: Prime Frog.

Problem Statement:
    Susan has a prime frog.
    Her frog is jumping around over 500 squares numbered 1 to 500. He can only
    jump one square to the left or to the right, with equal probability, and
    he cannot jump outside the range [1,500]. (If it lands at either end, it
    automatically jumps to the only available square on the next move.)
    When he is on a square with a prime number on it, he croaks 'P' (PRIME)
    with probability 2/3 or 'N' (NOT PRIME) with probability 1/3 just before
    jumping to the next square. When he is on a square with a number that is
    not prime he croaks 'P' with probability 1/3 or 'N' with probability 2/3
    just before jumping to the next square.
    Given that the frog's starting position is random with equal probability
    for every square, and given that she listens to his first 15 croaks, what
    is the probability that she hears the sequence PPPPNNPPPNPPNPN?
    Give your answer as a fraction p/q in reduced form.

Solution Approach:
    Model this as a hidden Markov model: 500 hidden states (positions 1..500)
    with tridiagonal transition probabilities (left/right neighbors, reflecting
    at the ends) and emission probabilities depending only on whether the
    state index is prime. Use the forward algorithm (dynamic programming)
    to compute the probability of the observed sequence from a uniform start.
    Use exact rational arithmetic (fractions or integer numerators/denoms)
    to produce the reduced fraction p/q. Time O(L*S) and O(S) memory (L=15,
    S=500), easily feasible.

Answer: ...
URL: https://projecteuler.net/problem=329
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 329
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'squares': 10, 'sequence': 'PPPP'}},
    {'category': 'main', 'input': {'squares': 500, 'sequence': 'PPPPNNPPPNPPNPN'}},
    {'category': 'extra', 'input': {'squares': 1000, 'sequence': 'PPPPNNPPPNPPNPN'}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_frog_p0329_s0(*, squares: int, sequence: str) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))