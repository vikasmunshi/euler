#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 48: Self powers

Problem Statement:
The series, 1¹ + 2² + 3³ + ... + 10¹⁰ = 10,405,071,317.

Find the last ten digits of the series, 1¹ + 2² + 3³ + ... + 1000¹⁰⁰⁰.

Solution Approach:
Unlike some series problems, there is no known closed-form formula for the sum of i^i from i=1 to n.
This solution utilizes Python's built-in support for arbitrary-precision integers to:

1. Calculate each term in the series (i^i) directly using modular exponentiation
2. Sum all terms in the series from 1¹ to n^n, maintaining only the last 10 digits at each step
3. Extract only the last 10 digits by applying modulo 10¹⁰ throughout the computation

While the intermediate values grow extremely large (1000¹⁰⁰⁰ has approximately 3000 digits),
using modular arithmetic at each step keeps the computation efficient by never working
with numbers larger than 10¹⁰.

Test Cases:
- For n=10: The sum equals 10,405,071,317, with last 10 digits 0,405,071,317
- For n=100: Last 10 digits are 9,027,641,920
- For n=1000: Last 10 digits are 9,110,846,700 (the answer)
- For n=10000: Last 10 digits are 6,237,204,500 (additional test)

URL: https://projecteuler.net/problem=48
Answer: 9110846700
"""

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=48)
problem_number: int = 48

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 10 ** 1}, answer=405071317, ),
    ProblemArgs(kwargs={'n': 10 ** 2}, answer=9027641920, ),
    ProblemArgs(kwargs={'n': 10 ** 3}, answer=9110846700, ),
    ProblemArgs(kwargs={'n': 10 ** 4}, answer=6237204500, ),
    ProblemArgs(kwargs={'n': 10 ** 5}, answer=3031782500, ),
    ProblemArgs(kwargs={'n': 10 ** 6}, answer=4077562500, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def last_ten_digits_self_power_series(*, n: int) -> int:
    """
    # Note: For extremely large values of n, this computation could be parallelized
    # by splitting the range into chunks and processing them concurrently, then combining
    # the results. However, for the given constraints (n ≤ 10000), the sequential
    # approach is already efficient.
    Calculate the last ten digits of the sum of self-powers series.

    This function computes the sum of the series 1¹ + 2² + 3³ + ... + n^n and returns
    only the last ten digits by applying modulo 10¹⁰ throughout the calculation.

    The implementation uses Python's built-in pow() function with the modulo argument
    for efficient modular exponentiation, which is significantly faster than the naive
    approach of calculating the full i^i value for large values of i.

    Args:
        n: The upper limit of the series (inclusive)

    Returns:
        The last ten digits of the sum

    Examples:
        >>> last_ten_digits_self_power_series(n=10)
        405071317  # Last 10 digits of 10,405,071,317
        >>> last_ten_digits_self_power_series(n=100)
        9027641920
        >>> last_ten_digits_self_power_series(n=1000)
        9110846700  # The answer to the main problem
    """
    modulo: int = 10 ** 10  # last 10 digits
    result: int = 0

    # Since there's no closed formula for the sum of i^i series,
    # we need to compute each term, but we can optimize using modular exponentiation
    for i in range(1, n + 1):
        # Calculate i^i mod 10^10 efficiently using modular exponentiation
        # This is more efficient for large values of i than direct computation
        term = pow(i, i, modulo)
        result = (result + term) % modulo
    return result


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
