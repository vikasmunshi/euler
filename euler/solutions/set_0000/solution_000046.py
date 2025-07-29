#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 46: goldbach_s_other_conjecture

Problem Statement:
  It was proposed by Christian Goldbach that every odd composite number can be
  written as the sum of a prime and twice a square. \begin{align} 9 = 7 + 2 *
  1^2\\ 15 = 7 + 2 * 2^2\\ 21 = 3 + 2 * 3^2\\ 25 = 7 + 2 * 3^2\\ 27 = 19 + 2 *
  2^2\\ 33 = 31 + 2 * 1^2 \end{align} It turns out that the conjecture was false.
  What is the smallest odd composite that cannot be written as the sum of a prime
  and twice a square?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=46
Answer: None
"""
from __future__ import annotations

from typing import Dict, List, Set

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=5777,
        is_main_case=False,
        kwargs={},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #46
@register_solution(problem_number=46, test_cases=test_cases)
def goldbach_s_other_conjecture() -> int:
    """
    Find the smallest odd composite number that disproves Goldbach's conjecture.

    This solution searches for the first counterexample to Goldbach's conjecture, which
    states that every odd composite number can be expressed as the sum of a prime and
    twice a square (n = p + 2s²). The algorithm efficiently generates primes and tests
    each odd composite number against all smaller primes.

    Returns:
        The smallest odd composite number that cannot be expressed as p + 2s²

    Example:
        >>> goldbach_s_other_conjecture()
        5777

    Note:
        The algorithm uses a modified sieve of Eratosthenes approach to efficiently
        generate prime numbers while simultaneously testing odd composite numbers
        against the conjecture.
    """
    primes: Set[int] = set()
    known_composites: Dict[int, List[int]] = dict()
    current_number = 2
    while True:
        if current_number not in known_composites:  # is a new prime
            primes.add(current_number)
            known_composites[current_number ** 2] = [current_number]  # Eratosthene's seive
        else:
            if current_number % 2 != 0:  # is odd composite
                # check half of current number minus all smaller prime is a perfect square
                if not any((((current_number - p) / 2) ** 0.5) % 1 == 0 for p in primes if current_number > p != 2):
                    return current_number
            for p in known_composites[current_number]:
                known_composites.setdefault(p + current_number, []).append(p)
            del known_composites[current_number]
        current_number += 1


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(46))
