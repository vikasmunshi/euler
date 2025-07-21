#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 26: Reciprocal cycles

Problem Statement:
A unit fraction contains 1 in the numerator. The decimal representation of the unit fractions
with denominators 2 to 10 are given:

1/2 = 0.5
1/3 = 0.(3)
1/4 = 0.25
1/5 = 0.2
1/6 = 0.1(6)
1/7 = 0.(142857)
1/8 = 0.125
1/9 = 0.(1)
1/10 = 0.1

Where 0.1(6) means 0.166666..., and has a 1-digit recurring cycle. It can be seen that 1/7
has a 6-digit recurring cycle.

Find the value of d < 1000 for which 1/d contains the longest recurring cycle in its decimal
fraction part.

Solution Approach:
This implementation uses number theory to efficiently find the answer. For a fraction 1/d,
the length of its recurring decimal cycle equals the multiplicative order of 10 modulo d
(when gcd(10, d) = 1). The multiplicative order is the smallest positive integer k such
that 10^k ≡ 1 (mod d).

To optimize the search:
1. We only consider values where gcd(d, 10) = 1 (d not divisible by 2 or 5)
2. We search in descending order from the upper bound, as larger primes tend to have longer cycles
3. We use the walrus operator (:=) to efficiently assign and test values in a single expression

Test Cases:
- For max_val=10, the answer is 7 (1/7 has a 6-digit cycle)
- For max_val=100, the answer is 97 (1/97 has a 96-digit cycle)
- For max_val=1000, the answer is 983 (1/983 has a 982-digit cycle)

URL: https://projecteuler.net/problem=26
Answer: 983
"""

from math import gcd
from typing import Optional

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=26)
problem_number: int = 26

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_val': 10},  # Small test case: find the longest cycle for d < 10
        answer=7,  # 1/7 has a 6-digit cycle: 0.(142857)
    ),
    ProblemArgs(
        kwargs={'max_val': 100},  # Medium test case: find the longest cycle for d < 100
        answer=97,  # 1/97 has a 96-digit cycle
    ),
    ProblemArgs(
        kwargs={'max_val': 1000},  # Full problem: find the longest cycle for d < 1000
        answer=983,  # 1/983 has a 982-digit cycle
    ),
    ProblemArgs(
        kwargs={'max_val': 10000},  # Full problem: find the longest cycle for d < 10000
        answer=9967,  # 1/9967 has a 9966-digit cycle
    ),
]


def multiplicative_order(a: int, modulus: int) -> Optional[int]:
    """
    Calculate the multiplicative order of a modulo modulus.

    The multiplicative order is the smallest positive integer k such that a^k ≡ 1 (mod modulus).
    For decimal fractions 1/d, the length of the recurring cycle equals the multiplicative
    order of 10 modulo d (when gcd(10, d) = 1).

    Args:
        a: The base number (for decimal fractions, this is 10)
        modulus: The modulus to calculate against (the denominator d)

    Returns:
        The multiplicative order if it exists within modulus iterations, None otherwise
    """
    r = 1
    for k in range(1, modulus):
        r = (r * a) % modulus
        if r == 1:
            return k
    else:
        return None


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def max_recurring_reciprocal_decimal_cycle(*, max_val: int) -> int:
    """
    Find the value of d < max_val with the longest recurring decimal cycle in 1/d.

    This solution uses number theory to efficiently find the denominator with the longest
    recurring cycle. It leverages the fact that for a fraction 1/d, the length of its recurring
    decimal cycle equals the multiplicative order of 10 modulo d (when gcd(10, d) = 1).

    Args:
        max_val: The upper bound for d (exclusive)

    Returns:
        The value of d < max_val for which 1/d has the longest recurring decimal cycle

    Example:
        >>> max_recurring_reciprocal_decimal_cycle(max_val=10)
        7  # 1/7 has a 6-digit recurring cycle: 0.(142857)
        >>> max_recurring_reciprocal_decimal_cycle(max_val=1000)
        983  # 1/983 has a 982-digit recurring cycle
    """
    # Using walrus operator ":=" to assign and test d in a single expression
    # Starting from max_val and checking in descending order (more efficient)
    # Only considering values where gcd(d, 10) = 1 (not divisible by 2 or 5)
    return max((multiplicative_order(a=10, modulus=d), d)
               for i in range(max(max_val // 10, 10))
               if (d := max_val - i) > 6 and gcd(d, 10) == 1)[1]


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
