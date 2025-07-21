# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 71:

Problem Statement:
Consider the fraction, n/d, where n and d are positive integers.
If n < d and HCF(n,d)=1, it is called a reduced proper fraction.

If we list the set of reduced proper fractions for d < 8 in ascending order of size, we get:
1/8, 1/7, 1/6, 1/5, 1/4, 2/7, 1/3, 3/8, 2/5, 3/7, 1/2, 4/7, 3/5, 5/8, 2/3, 5/7, 3/4, 4/5, 5/6, 6/7, 7/8

It can be seen that 2/5 is the fraction immediately to the left of 3/7.

By listing the set of reduced proper fractions for d < 1 000 000 in ascending order of size,
find the numerator of the fraction immediately to the left of 3/7.

Solution Approach:
To find the fraction immediately to the left of 3/7 in the ordered set of reduced proper fractions,
we need to find a fraction n/d that is:
1. Less than 3/7
2. As close as possible to 3/7
3. In its lowest form (HCF(n,d)=1)
4. Where d < max_d (the constraint given in the problem)

The key mathematical insight allows us to solve this problem with a direct calculation:

1. For a fraction to be as close as possible to 3/7 but still less than it, we need to subtract
   the smallest possible amount from 3/7

2. When we subtract 1/k from 3/7, we get:
   3/7 - 1/k = (3k - 7)/7k

3. For the result to be in lowest form, 7k must be divisible by 7, which means k must be divisible by 7

4. Therefore, we need the largest multiple of 7 that is less than max_d

5. If we call this value d = 7*(max_d//7), then our answer is the numerator of:
   3/7 - 1/d = (3d - 7)/7d

This avoids the need to generate all fractions or iterate through multiple combinations,
making the solution extremely efficient even for very large inputs.

Test Cases:

URL: https://projecteuler.net/problem=71
Answer: 428570
"""
from fractions import Fraction

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=71)
problem_number: int = 71

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_d': 10 ** 1}, answer=2, ),
    ProblemArgs(kwargs={'max_d': 10 ** 6}, answer=428570, ),
    ProblemArgs(kwargs={'max_d': 10 ** 9}, answer=428571425, ),
    ProblemArgs(kwargs={'max_d': 10 ** 12}, answer=428571428570, ),
]


# Register this function as a solution for problem #71 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def reduced_fraction_left_of_3_over_7(*, max_d: int) -> int:
    """Find the numerator of the reduced proper fraction immediately to the left of 3/7.

    The function uses a direct mathematical approach to efficiently find the fraction
    immediately to the left of 3/7 with denominator < max_d.

    Mathematical approach:
    1. We start with our target fraction 3/7
    2. To get as close as possible to 3/7 but still below it, we need the denominator
       to be divisible by 7 (to ensure the result is in lowest form)
    3. We find the largest multiple of 7 that is less than max_d
    4. The fraction (3/7 - 1/largest_multiple_of_7) gives us the closest reduced
       proper fraction to the left of 3/7

    Args:
        max_d: The maximum denominator value to consider

    Returns:
        The numerator of the fraction immediately to the left of 3/7
    """
    result: Fraction = Fraction(3, 7) - Fraction(1, 7 * (max_d // 7))
    if show_solution():
        difference = Fraction(3, 7) - result
        print(f'Solution for {max_d=}: {result=} {difference=} {result.numerator=}')
    return result.numerator


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
