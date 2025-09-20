#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 758: Buckets of Water.

Problem Statement:
    There are 3 buckets labelled S (small) of 3 litres, M (medium) of 5 litres and L (large)
    of 8 litres.
    Initially S and M are full of water and L is empty.
    By pouring water between the buckets exactly one litre of water can be measured.
    Since there is no other way to measure, once a pouring starts it cannot stop until
    either the source bucket is empty or the destination bucket is full.
    At least four pourings are needed to get one litre:
        (3,5,0) -> M to L -> (3,0,5) -> S to M -> (0,3,5) -> L to S -> (3,3,2)
        -> S to M -> (1,5,2)
    After these operations, there is exactly one litre in bucket S.

    In general the sizes of the buckets S, M, L are a, b, a + b litres, respectively.
    Initially S and M are full and L is empty. If the above rule of pouring still applies
    and a and b are two coprime positive integers with a ≤ b then it is always possible to
    measure one litre in finitely many steps.

    Let P(a,b) be the minimal number of pourings needed to get one litre. Thus P(3,5)=4.
    Also, P(7, 31)=20 and P(1234, 4321)=2780.

    Find the sum of P(2^(p^5)-1, 2^(q^5)-1) for all pairs of prime numbers p,q such that
    p < q < 1000. Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=758
"""
from typing import Any

euler_problem: int = 758
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'xC6lXLzhkx4='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
