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

Solution Approach:
    Model the problem as a multi-type branching process with k types.
    Use recursive probability equations to find extinction probabilities P_k,m.
    Employ linear algebra / fixed point iteration or root-finding methods for the
    extinction vector.
    The sequence r_n mod 5 defines the transition probabilities governing offspring.
    Careful use of modular arithmetic and efficient iteration is essential.
    Expected complexity depends on k*m but can be optimized with memoization.

Answer: ...
URL: https://projecteuler.net/problem=666
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 666
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 2, 'm': 2}},
    {'category': 'main', 'input': {'k': 500, 'm': 10}},
    {'category': 'extra', 'input': {'k': 1000, 'm': 10}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_polymorphic_bacteria_p0666_s0(*, k: int, m: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))