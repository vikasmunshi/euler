# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 12: Highly Divisible Triangular Number

Problem Statement:
The sequence of triangle numbers is generated by adding the natural numbers. So the 7th triangle number
would be 1 + 2 + 3 + 4 + 5 + 6 + 7 = 28. The first ten terms would be:
1, 3, 6, 10, 15, 21, 28, 36, 45, 55, ...

Let us list the factors of the first seven triangle numbers:
1: 1
3: 1, 3
6: 1, 2, 3, 6
10: 1, 2, 5, 10
15: 1, 3, 5, 15
21: 1, 3, 7, 21
28: 1, 2, 4, 7, 14, 28

We can see that 28 is the first triangle number to have over five divisors.
What is the value of the first triangle number to have over five hundred divisors?

Solution Approach:
This solution employs mathematical optimizations to efficiently find triangle numbers with many divisors:

1. Triangle Number Generation: Each triangle number is calculated using the efficient formula
   n(n+1)/2, which avoids summing all numbers from 1 to n explicitly.

2. Divisor Counting Optimization: Rather than checking all numbers from 1 to n as potential
   divisors, we only check up to the square root of n. For each divisor i found, we count
   both i and n/i as divisors, effectively cutting the search space in half.

3. Special Case Handling: When n is a perfect square, we handle it specially to avoid
   counting the square root twice.

4. Iterative Search: We generate triangle numbers in sequence and check each one until
   finding the first with more than the required number of divisors.

The time complexity is O(T·√T) where T is the target triangle number, as we check up to
√T potential divisors for each triangle number examined.

Test Cases:
- For num_divisors=5: The first triangle number with more than 5 divisors is 28
- For num_divisors=500: The first triangle number with more than 500 divisors is 76576500

URL: https://projecteuler.net/problem=12
Answer: 76576500
"""
from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=12)
problem_number: int = 12

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'num_divisors': 5}, answer=28, ),
    ProblemArgs(kwargs={'num_divisors': 500}, answer=76576500, ),
]


def num_factors(n: int) -> int:
    """Calculate the number of factors (divisors) for a given integer.

    This function uses an optimized approach that only checks divisors up to the square root of n.
    For each divisor 'i' found below sqrt(n), we count both i and n/i as factors.
    This gives us a 2x speedup compared to checking all numbers from 1 to n.
    The 1 is added at the beginning (to count 1 as a factor), and n is counted implicitly.
    We handle perfect-squares specially by subtracting 1 when sqrt(n) is a divisor to avoid counting it twice.

    Args:
        n: A positive integer

    Returns:
        The total number of factors (divisors) of n
    """
    return 1 + 2 * sum([1 for i in range(2, int(n ** 0.5) + 1) if n % i == 0]) - (1 if n % int(n ** 0.5) == 0 else 0)


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def smallest_triangle_number(*, num_divisors: int) -> int:
    """
    Find the first triangle number with more than the specified number of divisors.

    This function iteratively generates triangle numbers and checks each one until
    finding the first that has more than the required number of divisors.

    Args:
        num_divisors: The minimum number of divisors required

    Returns:
        The first triangle number that has more than num_divisors divisors

    Algorithm:
        1. Start with the first triangle number (1)
        2. For each triangle number, count its divisors using the optimized num_factors function
        3. If the count exceeds num_divisors, return the current triangle number
        4. Otherwise, generate the next triangle number using the formula n(n+1)/2
        5. Repeat until a triangle number with sufficient divisors is found

    Examples:
        >>> smallest_triangle_number(num_divisors=5)
        28  # First triangle number with over 5 divisors
        >>> smallest_triangle_number(num_divisors=500)
        76576500  # First triangle number with over 500 divisors
    """
    i, triangle_number = 1, 1
    while num_factors(triangle_number) < num_divisors:
        i += 1
        triangle_number = i * (i + 1) // 2

    return triangle_number


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
