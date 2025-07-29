#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 69: totient_maximum

Problem Statement:
  Euler's totient function, \phi(n) [sometimes called the phi function], is
  defined as the number of positive integers not exceeding n which are relatively
  prime to n. For example, as 1, 2, 4, 5, 7, and 8, are all less than or equal to
  nine and relatively prime to nine, \phi(9)=6.  n Relatively Prime \phi(n)
  n/\phi(n) 2 1 1 2 3 1,2 2 1.5 4 1,3 2 2 5 1,2,3,4 4 1.25 6 1,5 2 3 7 1,2,3,4,5,6
  6 1.1666... 8 1,3,5,7 4 2 9 1,2,4,5,7,8 6 1.5 10 1,3,7,9 4 2.5  It can be seen
  that n = 6 produces a maximum n/\phi(n) for n\leq 10. Find the value of n\leq
  1\,000\,000 for which n/\phi(n) is a maximum.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=69
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.primes import gen_primes_sieve
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=6,
        is_main_case=False,
        kwargs={'n': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=30,
        is_main_case=False,
        kwargs={'n': 100},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=210,
        is_main_case=False,
        kwargs={'n': 1000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=2310,
        is_main_case=False,
        kwargs={'n': 10000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=30030,
        is_main_case=False,
        kwargs={'n': 100000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=510510,
        is_main_case=False,
        kwargs={'n': 1000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=9699690,
        is_main_case=False,
        kwargs={'n': 10000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=9699690,
        is_main_case=False,
        kwargs={'n': 100000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=223092870,
        is_main_case=False,
        kwargs={'n': 1000000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=6469693230,
        is_main_case=False,
        kwargs={'n': 10000000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=6469693230,
        is_main_case=False,
        kwargs={'n': 100000000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=200560490130,
        is_main_case=False,
        kwargs={'n': 1000000000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #69
@register_solution(problem_number=69, test_cases=test_cases)
def totient_maximum(*, n: int) -> int:
    """Find the value ≤ n for which n/φ(n) is a maximum.

    This solution leverages a key mathematical insight about Euler's totient function:
    To maximize n/φ(n), we want to include as many distinct prime factors as possible,
    starting with the smallest primes.

    The algorithm works by multiplying consecutive primes (2, 3, 5, 7, 11, ...) until
    the product exceeds the limit n, then divides by the last prime to get the largest
    valid product. This approach gives us the number with the maximum value of n/φ(n)
    that doesn't exceed the given limit.

    Why this works:
    1. For any number n with prime factorization p₁^k₁ * p₂^k₂ * ... * pᵣ^kᵣ:
       n/φ(n) = ∏(pᵢ/(pᵢ-1)) for all distinct prime factors pᵢ
    2. Each distinct prime factor increases n/φ(n)
    3. Smaller primes have a larger effect (e.g., 2/(2-1) = 2 > 3/(3-1) = 1.5)
    4. Prime powers don't help (adding p^k instead of a new prime p' is less optimal)

    Args:
        n: The upper limit for the search

    Returns:
        The value ≤ n that maximizes n/φ(n)
    """
    result: int = 1
    for prime_num in gen_primes_sieve():
        # Multiply by each consecutive prime
        if (result := result * prime_num) > n:
            # If we exceed the limit, backtrack by dividing by the last prime
            result = result // prime_num
            break
    return result


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(69))
