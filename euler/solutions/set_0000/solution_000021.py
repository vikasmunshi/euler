#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 21: amicable_numbers

Problem Statement:
  Let d(n) be defined as the sum of proper divisors of n (numbers less than n
  which divide evenly into n). If d(a) = b and d(b) = a, where a \ne b, then a and
  b are an amicable pair and each of a and b are called amicable numbers. For
  example, the proper divisors of 220 are 1, 2, 4, 5, 10, 11, 20, 22, 44, 55 and
  110; therefore d(220) = 284. The proper divisors of 284 are 1, 2, 4, 71 and 142;
  so d(284) = 220. Evaluate the sum of all the amicable numbers under 10000.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=21
Answer: None
"""
from __future__ import annotations

from functools import lru_cache

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=31626,
        is_main_case=False,
        kwargs={'max_num': 10000},
        solution_execution_time=None,
        solved=False
    ),
]


@lru_cache()
def sum_factors(n: int) -> int:
    """Calculate the sum of proper divisors (factors) of n.

    This optimized implementation finds all divisors by iterating only up to the square root of n.
    For each divisor i, we also include n//i as a divisor, avoiding duplicate counting of perfect squares.
    The function returns the sum of all proper divisors (excluding n itself).

    Algorithm Details:
    1. Start with 1 as it's always a proper divisor
    2. Iterate from 2 to sqrt(n):
       a. If i divides n evenly, add both i and n/i to the sum
       b. Special case: if i² = n, only count i once (avoid counting the square root twice)
    3. Return the total sum

    Mathematical Background:
    A proper divisor of n is any positive integer that divides n evenly and is less than n.
    For example, the proper divisors of 12 are 1, 2, 3, 4, and 6, with a sum of 16.

    Optimizations:
    - Square root limit: We only need to check divisors up to sqrt(n) and derive their pairs
    - Memoization: The @lru_cache decorator stores results of previous calculations,
      dramatically improving performance for repeated calls
    - Perfect square handling: We subtract the square root if n is a perfect square to avoid
      counting it twice

    Complexity Analysis:
    - Time Complexity: O(√n) - we only iterate up to the square root of n
    - Space Complexity: O(k) where k is the number of unique inputs due to memoization

    Args:
        n: A positive integer whose proper divisors will be summed

    Returns:
        The sum of all proper divisors of n

    Examples:
        >>> sum_factors(220)
        284  # Sum of 1+2+4+5+10+11+20+22+44+55+110
        >>> sum_factors(284)
        220  # Sum of 1+2+4+71+142
    """
    n_sqrt = int(n ** 0.5)
    return 1 + sum(i + n // i for i in range(2, n_sqrt + 1) if n % i == 0) - (n_sqrt if n_sqrt ** 2 == n else 0)


# Register this function as a solution for problem #21
@register_solution(problem_number=21, test_cases=test_cases)
def amicable_numbers(*, max_num: int) -> int:
    """Find the sum of all amicable numbers under max_num.

    An amicable number pair (a,b) exists when sum_factors(a) = b and sum_factors(b) = a,
    where a ≠ b. This function checks each number up to max_num, computes its proper
    divisor sum (d(x)), and checks if d(d(x)) = x while ensuring x ≠ d(x) to avoid
    perfect numbers (which are not amicable numbers).

    Historical Note:
    Amicable numbers have been studied since antiquity and were considered to have mystical
    properties by early mathematicians. Pythagoras knew of the pair (220,284), and amicable
    numbers play a role in number theory and recreational mathematics.

    Implementation Details:
    1. For each number x from 2 to max_num:
       a. Compute y = d(x) (sum of proper divisors of x)
       b. Check if x ≠ y to exclude perfect numbers (where d(x) = x)
       c. Check if d(y) = x to confirm the amicable relationship
       d. If both conditions are met, include x in the sum

    Note that this approach will count each number in an amicable pair individually when
    they're both below max_num. This is correct for the problem's requirements, as we need
    the sum of all amicable numbers (not pairs) below max_num.

    The walrus operator (:=) is used to efficiently compute and store d(x) for later comparison,
    avoiding redundant calculation. Together with the memoized sum_factors function, this makes
    the solution highly efficient.

    Complexity Analysis:
    - Time Complexity: O(max_num × √max_num) where each call to sum_factors is O(√n)
    - Space Complexity: O(max_num) for storing memoized results in sum_factors

    Args:
        max_num: Upper limit for finding amicable numbers

    Returns:
        Sum of all amicable numbers below max_num

    Examples:
        Known amicable pairs under 10,000 include:
        - (220, 284): d(220) = 284, d(284) = 220
        - (1184, 1210): d(1184) = 1210, d(1210) = 1184
        - (2620, 2924): d(2620) = 2924, d(2924) = 2620
        - (5020, 5564): d(5020) = 5564, d(5564) = 5020
        - (6232, 6368): d(6232) = 6368, d(6368) = 6232

        >>> amicable_numbers(max_num=1000)  # Finds amicable numbers 220 and 284 below 1000
        504  # 220 + 284 = 504
    """
    return sum(x for x in range(2, max_num + 1) if (y := sum_factors(x)) != x and sum_factors(y) == x)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(21))
