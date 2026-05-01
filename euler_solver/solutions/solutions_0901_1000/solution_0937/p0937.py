#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 937: Equiproduct Partition.

Problem Statement:
    Let θ=√-2.

    Define T to be the set of numbers of the form a+bθ, where a and b are integers
    and either a>0, or a=0 and b>0. For a set S ⊆ T and element z ∈ T, define p(S,z)
    to be the number of ways of choosing two distinct elements from S with product
    either z or -z.

    For example if S={1,2,4} and z=4, there is only one valid pair of elements with
    product ±4, namely 1 and 4. Thus, in this case p(S,z)=1.

    For another example, if S={1,θ,1+θ,2-θ} and z=2-θ, we have 1·(2-θ)=z and
    θ·(1+θ)=-z, giving p(S,z)=2.

    Let A and B be two sets satisfying the following conditions:
        1 ∈ A
        A ∩ B = ∅
        A ∪ B = T
        p(A,z) = p(B,z) for all z ∈ T

    Remarkably, these four conditions uniquely determine the sets A and B.

    Let F_n be the set of the first n factorials: F_n={1!, 2!, ..., n!}, and define
    G(n) to be the sum of all elements of F_n ∩ A.

    You are given G(4) = 25, G(7) = 745, and G(100) ≡ 709772949 (mod 10^9+7).

    Find G(10^8) and give your answer modulo 10^9+7.

URL: https://projecteuler.net/problem=937
"""
from typing import Any

euler_problem: int = 937
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
    'ZoW2k1TNfhhmSmMXZA2hbXHaggI='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
