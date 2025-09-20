#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 866: Tidying Up B.

Problem Statement:
    A small child has a “number caterpillar” consisting of N jigsaw pieces,
    each with one number on it, which, when connected together in a line,
    reveal the numbers 1 to N in order.

    Every night, the child's father has to pick up the pieces of the caterpillar
    that have been scattered across the play room. He picks up the pieces at
    random and places them in the correct order.
    As the caterpillar is built up in this way, it forms distinct segments that
    gradually merge together.

    Any time the father places a new piece in its correct position, a segment
    of length k is formed and he writes down the k-th hexagonal number
    k*(2k-1). Once all pieces have been placed and the full caterpillar
    constructed he calculates the product of all the numbers written down.
    Interestingly, the expected value of this product is always an integer.
    For example if N=4 then the expected value is 994.

    Find the expected value of the product for a caterpillar of N=100 pieces.
    Give your answer modulo 987654319.

URL: https://projecteuler.net/problem=866
"""
from typing import Any

euler_problem: int = 866
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
