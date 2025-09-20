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

URL: https://projecteuler.net/problem=329
"""
from typing import Any

euler_problem: int = 329
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'squares': 10, 'sequence': 'PPPP'}, 'answer': None},
    {'category': 'main', 'input': {'squares': 500, 'sequence': 'PPPPNNPPPNPPNPN'}, 'answer': None},
    {'category': 'extra', 'input': {'squares': 1000, 'sequence': 'PPPPNNPPPNPPNPN'}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
