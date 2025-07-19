#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 47: Distinct primes factors

Problem Statement:
The first two consecutive numbers to have two distinct prime factors are:
14 = 2 × 7
15 = 3 × 5

The first three consecutive numbers to have three distinct prime factors are:
644 = 2² × 7 × 23
645 = 3 × 5 × 43
646 = 2 × 17 × 19

Find the first four consecutive integers to have four distinct prime factors each.
What is the first of these numbers?

Solution Approach:
This solution uses a straightforward approach to find sequences of consecutive integers
with specific prime factorization properties:

1. Define a helper function that counts the number of distinct prime factors for any number
2. Iterate through integers starting from 2
3. For each number, check if it and the next n-1 consecutive integers all have
   exactly n distinct prime factors
4. Return the first number that satisfies this condition

We use efficient iteration with itertools.count and a generator expression to
minimize memory usage while testing large sequences of numbers.

Test Cases:
- For n=2: First sequence is [14, 15] (verified in problem statement)
- For n=3: First sequence is [644, 645, 646] (verified in problem statement)
- For n=4: First sequence is [134043, 134044, 134045, 134046] (our answer)

URL: https://projecteuler.net/problem=47
Answer: 134043
"""
from itertools import count

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.primes import prime_factor_count

# The problem number from Project Euler (https://projecteuler.net/problem=47)
problem_number: int = 47

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 2},  # First 2 consecutive integers with 2 distinct prime factors
        answer=14,  # 14=2×7 and 15=3×5
    ),
    ProblemArgs(
        kwargs={'n': 3},  # First 3 consecutive integers with 3 distinct prime factors
        answer=644,  # 644=2²×7×23, 645=3×5×43, 646=2×17×19
    ),
    ProblemArgs(
        kwargs={'n': 4},  # First 4 consecutive integers with 4 distinct prime factors
        answer=134043,  # The answer to the main problem
    ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def first_of_n_consecutive_integers_with_n_prime_factors(n: int) -> int:
    """
    Find the first of n consecutive integers, each with exactly n distinct prime factors.

    This solution searches for sequences of consecutive integers with specific prime
    factorization properties. It efficiently iterates through integers and checks if
    each number in a consecutive sequence has exactly the required number of distinct
    prime factors.

    Args:
        n: The parameter defining both the length of the consecutive sequence and
           the number of distinct prime factors required for each integer

    Returns:
        The first integer in the sequence of n consecutive integers with the required property

    Examples:
        >>> first_of_n_consecutive_integers_with_n_prime_factors(2)  # First sequence with 2 factors each
        14              # 14=2×7 and 15=3×5
        >>> first_of_n_consecutive_integers_with_n_prime_factors(3)  # First sequence with 3 factors each
        644             # 644=2²×7×23, 645=3×5×43, 646=2×17×19
        >>> first_of_n_consecutive_integers_with_n_prime_factors(4)  # First sequence with 4 factors each
        134043          # The answer to the main problem
    """
    return next(number for number in count(2) if not any(prime_factor_count(number + i) != n for i in range(0, n)))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
