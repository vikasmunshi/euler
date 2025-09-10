#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 367: Bozo Sort.

Problem Statement:
    Bozo sort, not to be confused with bogo sort, repeatedly checks whether the
    input sequence is sorted and, if not, swaps two randomly chosen elements.
    This is repeated until the sequence is sorted.

    If we consider all permutations of the first 4 natural numbers as input,
    the expected number of swaps, averaged over all 4! input sequences, is
    24.75. The already sorted sequence takes 0 steps.

    This problem uses a variant: if the sequence is not sorted we pick three
    elements uniformly at random and apply a uniformly random permutation of
    these three elements (all 3! = 6 permutations equally likely). The already
    sorted sequence takes 0 steps. For n = 4 the averaged expected number of
    such shuffles is 27.5.

    Consider all permutations of the first 11 natural numbers. Averaged over
    all 11! input sequences, what is the expected number of shuffles this
    algorithm will perform?

    Give your answer rounded to the nearest integer.

Solution Approach:
    Model the process as a Markov chain on permutations with the sorted
    permutation absorbing. Use group symmetry to aggregate states by cycle
    type (conjugacy classes), reducing the state space to integer partitions
    of n (p(n) states). Derive linear equations E(s)=1+sum_t P(s->t) E(t) for
    non-absorbing classes and solve the linear system. Weight class values by
    class sizes to obtain the uniform-average expectation. Complexity about
    O(p(n)^3) for solving the dense linear system; exact rationals or high
    precision floats recommended.

Answer: ...
URL: https://projecteuler.net/problem=367
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 367
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}},
    {'category': 'main', 'input': {'n': 11}},
    {'category': 'extra', 'input': {'n': 12}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_bozo_sort_p0367_s0(*, n: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))