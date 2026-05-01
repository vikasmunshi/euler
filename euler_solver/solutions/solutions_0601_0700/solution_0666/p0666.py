#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 666: Polymorphic Bacteria.

Problem Statement:
    Members of a species of bacteria occur in two different types: alpha and beta.
    Individual bacteria are capable of multiplying and mutating between the types
    according to the following rules:

        - Every minute, each individual will simultaneously undergo some kind of
          transformation.
        - Each individual A of type alpha will, independently, do one of the following
          (at random with equal probability):
            * Clone itself, resulting in a new bacterium of type alpha (alongside A who remains).
            * Split into 3 new bacteria of type beta (replacing A).
        - Each individual B of type beta will, independently, do one of the following
          (at random with equal probability):
            * Spawn a new bacterium of type alpha (alongside B who remains).
            * Die.

    If a population starts with a single bacterium of type alpha, then it can be shown
    that there is a 0.07243802 probability that the population will eventually die out,
    and a 0.92756198 probability that the population will last forever. These probabilities
    are given rounded to 8 decimal places.

    Now consider another species of bacteria, S_k,m (where k and m are positive integers),
    which occurs in k different types alpha_i for 0 <= i < k. The rules governing this
    species' lifecycle involve the sequence r_n defined by:

        r_0 = 306
        r_{n+1} = r_n^2 mod 10007

    Every minute, for each i, each bacterium A of type alpha_i will independently choose
    an integer j uniformly at random in the range 0 <= j < m. What it then does depends
    on q = r_{i*m+j} mod 5:

        If q=0, A dies.
        If q=1, A clones itself, resulting in a new bacterium of type alpha_i (alongside A who remains).
        If q=2, A mutates, changing into type alpha_{(2*i) mod k}.
        If q=3, A splits into 3 new bacteria of type alpha_{(i^2+1) mod k} (replacing A).
        If q=4, A spawns a new bacterium of type alpha_{(i+1) mod k} (alongside A who remains).

    In fact, the original species was S_2,2, with alpha=alpha_0 and beta=alpha_1.

    Let P_k,m be the probability that a population of species S_k,m, starting with a
    single bacterium of type alpha_0, will eventually die out. So P_2,2 = 0.07243802.
    You are also given that P_4,3 = 0.18554021 and P_10,5 = 0.53466253, all rounded to
    8 decimal places.

    Find P_500,10, and give your answer rounded to 8 decimal places.

URL: https://projecteuler.net/problem=666
"""
from typing import Any

euler_problem: int = 666
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 2, 'm': 2}, 'answer': None},
    {'category': 'main', 'input': {'k': 500, 'm': 10}, 'answer': None},
    {'category': 'extra', 'input': {'k': 1000, 'm': 10}, 'answer': None},
]
encrypted: str = (
    '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'
    'exaK3FtN/veNunz9Is04nMd5xGGyoxNUrwC1ig=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
