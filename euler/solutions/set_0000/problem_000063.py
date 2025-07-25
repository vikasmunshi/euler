#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 63: Powerful Digit Counts

Problem Statement:
The 5-digit number, 16807=7^5, is also a fifth power. Similarly, the 9-digit number, 134217728=8^9, is a ninth power.
How many n-digit positive integers exist which are also an nth power?

Solution Approach:
This problem requires finding numbers where the number of digits equals the power to which the base is raised.
Key insights that drive the solution:

1. Mathematical Constraint: For a number b^n to have exactly n digits, it must satisfy:
   10^(n-1) ≤ b^n < 10^n
   This gives us bounds on the base b: (10^(n-1))^(1/n) ≤ b < (10^n)^(1/n)

2. Implementation Strategy:
   - For each power n, determine valid bases that produce n-digit numbers
   - Count all such numbers across all possible powers
   - We can stop when no valid bases exist for a given power

3. Optimization:
   - Since we want b^n to have exactly n digits, and b^n grows faster than the digit count for large b,
     we only need to check bases up to 9 (since 10^n has n+1 digits)
   - We need to start from n=1 and continue until no more valid values are found

The solution employs a systematic approach to find and count all n-digit nth powers without
exhaustive enumeration of large numbers.

URL: https://projecteuler.net/problem=63
Answer: 49
"""
from math import ceil
from typing import Tuple

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=63)
problem_number: int = 63

problem_args_list: ProblemArgsList = [ProblemArgs(kwargs={}, answer=49, ), ]


def n_digit_nth_powers(n: int) -> Tuple[int, ...]:
    """
    Generate all n-digit numbers that are also nth powers.

    This function finds all numbers b^n where b^n has exactly n digits. It calculates
    the valid range of bases that can produce such numbers and returns all resulting powers.

    Mathematical Derivation:
    - For a number to have exactly n digits, it must be in the range [10^(n-1), 10^n - 1]
    - For b^n to be in this range, we need: 10^(n-1) ≤ b^n < 10^n
    - Solving for b: (10^(n-1))^(1/n) ≤ b < (10^n)^(1/n)

    Args:
        n: The power to which bases will be raised (also the target digit count)

    Returns:
        A tuple containing all n-digit numbers that are also nth powers

    Examples:
        >>> n_digit_nth_powers(1)
        (1, 2, 3, 4, 5, 6, 7, 8, 9)  # All single-digit numbers that are 1st powers
        >>> n_digit_nth_powers(2)
        (16, 25, 36, 49, 64, 81)  # All 2-digit numbers that are 2nd powers
    """
    start_range: int = ceil((10 ** (n - 1)) ** (1 / n))
    stop_range: int = ceil(((10 ** n) - 1) ** (1 / n)) + 1
    return tuple(r for i in range(start_range, stop_range) if len(str(r := i ** n)) == n)


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def count_n_digit_numbers_also_nth_power() -> int:
    """
    Count all n-digit positive integers that are also nth powers.

    This function finds the total count of numbers that satisfy the property where
    a number with n digits is also an nth power (b^n). It systematically checks
    each power n, starting from 1, until no more valid solutions exist.

    The key insight is that for large enough n, there are no valid bases b where b^n
    has exactly n digits. This is because the digit count grows logarithmically with
    the value, while the value grows exponentially with the power.

    Mathematical Properties:
    - For b ≥ 10, b^n always has more than n digits
    - For b < 1, b^n is always less than 1
    - For b = 1, 1^n = 1 has 1 digit only when n = 1
    - For 1 < b < 10, b^n has exactly n digits for certain values of n

    Algorithm:
    1. Start with n = 1 and count all valid numbers
    2. Increment n and repeat until no more valid numbers are found
    3. Return the total count

    Returns:
        The total count of n-digit positive integers that are also nth powers

    Example:
        >>> count_n_digit_numbers_also_nth_power()
        49
    """
    result: int = 0
    n: int = 1
    while solutions := n_digit_nth_powers(n):
        result += len(solutions)
        n += 1
        if show_solution():
            print(f'{n=} {len(solutions)=} {solutions=} ')
    return result


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
