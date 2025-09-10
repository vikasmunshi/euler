#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 898: Claire Voyant.

Problem Statement:
    Claire Voyant is a teacher playing a game with a class of students.
    A fair coin is tossed on the table. All the students can see the outcome of
    the toss, but Claire cannot.
    Each student then tells Claire whether the outcome is head or tail. The students
    may lie, but Claire knows the probability that each individual student lies.
    Moreover, the students lie independently.

    After that, Claire attempts to guess the outcome using an optimal strategy.

    For example, for a class of four students with lying probabilities 20%, 40%,
    60%, 80%, Claire guesses correctly with probability 0.832.

    Find the probability that Claire guesses correctly for a class of 51 students
    each lying with a probability of 25%, 26%, ..., 75% respectively.

    Give your answer rounded to 10 digits after the decimal point.

Solution Approach:
    Use probability theory and optimal decision making under uncertainty.
    Model each student's response as a Bernoulli variable with known lying probability.
    Combine independent signals optimally via likelihood ratios or Bayesian inference.
    Calculate total probability of correct guess with dynamic programming or
    bitwise probability convolution.
    Time complexity depends on number of students and precision, but polynomial
    approach feasible.

Answer: ...
URL: https://projecteuler.net/problem=898
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 898
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'lying_probabilities': [0.2, 0.4, 0.6, 0.8]}},
    {'category': 'main', 'input': {'lying_probabilities': [i / 100 for i in range(25, 76)]}},
]

@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_claire_voyant_p0898_s0(*, lying_probabilities: list[float]) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))