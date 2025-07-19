# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 65: Convergents of e

Problem Statement:
The square root of 2 can be written as an infinite continued fraction.

√2 = 1 + 1/(2 + 1/(2 + 1/(2 + 1/(2 + ...))))

The infinite continued fraction can be written, √2 = [1; (2)], (2) indicates that 2 repeats ad infinitum.
In a similar way, √23 = [4; (1, 3, 1, 8)].

It turns out that the sequence of partial values of continued fractions for square roots provide the best rational
approximations. Let us consider the convergents for √2.

1 + 1/2 = 3/2
1 + 1/(2 + 1/2) = 7/5
1 + 1/(2 + 1/(2 + 1/2)) = 17/12
1 + 1/(2 + 1/(2 + 1/(2 + 1/2))) = 41/29

Hence the sequence of the first ten convergents for √2 are:

1, 3/2, 7/5, 17/12, 41/29, 99/70, 239/169, 577/408, 1393/985, 3363/2378, ...

What is most surprising is that the important mathematical constant,

e = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, ... , 1, 2k, 1, ...].

The first ten terms in the sequence of convergents for e are:

2, 3, 8/3, 11/4, 19/7, 87/32, 106/39, 193/71, 1264/465, 1457/536, ...

The sum of digits in the numerator of the 10th convergent is 1 + 4 + 5 + 7 = 17.

Find the sum of digits in the numerator of the 100th convergent of the continued fraction for e.

Solution Approach:
This problem involves calculating the continued fraction convergents for the mathematical constant e.
Our approach consists of several key steps:

1. Pattern Recognition: We identify that e has a special continued fraction representation
   [2; 1, 2, 1, 1, 4, 1, 1, 6, ...]
   where the pattern follows a cycle with every third term being 2k (where k increases by 1 each cycle)

2. Denominator Calculation: We implement a function e_den() that returns the denominator in the
   continued fraction expansion based on its position, following the pattern described above

3. Recursive Implementation: We use recursion to calculate the nth convergent by working backwards
   from the deepest level of the fraction to the outermost

4. Fraction Handling: We leverage Python's Fraction class to automatically manage the rational numbers
   and perform the necessary arithmetic operations

5. Final Calculation: We extract the numerator from the resulting fraction and calculate the sum of its digits

The recursive approach elegantly handles the continued fraction calculation without requiring explicit
formulation of the recurrence relation between consecutive convergents.

Test Cases:
- For the 10th convergent: Sum of digits in numerator = 17
- For the 100th convergent: Sum of digits in numerator = 272

URL: https://projecteuler.net/problem=65
Answer: 272
"""
from fractions import Fraction

from euler.evaluator import evaluate_solutions, register_solution
from euler.sys_utils import set_resource_limits
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.misc import sum_digits

# The problem number from Project Euler (https://projecteuler.net/problem=65)
problem_number: int = 65

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'convergent_num': 10 ** 1}, answer=17, ),
    ProblemArgs(kwargs={'convergent_num': 10 ** 2}, answer=272, ),
    ProblemArgs(kwargs={'convergent_num': 10 ** 3}, answer=4034, ),
    ProblemArgs(kwargs={'convergent_num': 10 ** 4}, answer=55322, ),
]


def e_denominator(n: int) -> int:
    """Calculate the nth denominator in the continued fraction expansion of e.

    This function implements the pattern for the continued fraction expansion of e,
    which follows [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, ...] where every third term is 2k
    (with k increasing by 1 each cycle), and all other terms are 1.

    Args:
        n: The position in the continued fraction expansion (1-indexed)

    Returns:
        The value of the nth term in e's continued fraction expansion

    Examples:
        >>> e_denominator(1)  # First term
        2
        >>> e_denominator(2)  # Second term
        1
        >>> e_denominator(3)  # Third term
        2
        >>> e_denominator(6)  # Sixth term
        4
    """
    if n == 1:
        return 2
    elif n % 3 == 0:
        return 2 * n // 3
    else:
        return 1


def nth_convergent_of_e(n: int, *, _n: int = 1) -> Fraction | int:
    """Recursively calculate the nth convergent of the continued fraction of e.

    This function uses a recursive approach to compute the continued fraction convergent,
    working from the deepest level of the fraction back to the outermost level. It builds
    the fraction representation using the pattern of denominators for e.

    The implementation uses tail recursion, working from the first term (at the outermost level)
    toward the nth term, then building the fraction back up as the recursion unwinds.

    Args:
        n: The convergent number to calculate (1-indexed)
        _n: Internal parameter for tracking the current position during recursion (default=1)

    Returns:
        The nth convergent of e as a Fraction object (or int for n=1)

    Implementation Notes:
        - Uses the e_den function to determine the value at each position
        - The recursion terminates when __n reaches n (the target convergent)
        - Python's Fraction class handles the rational arithmetic automatically

    """
    if n == _n:
        return e_denominator(_n)
    return e_denominator(_n) + Fraction(1, nth_convergent_of_e(n, _n=_n + 1))


@register_solution(problem_number=problem_number, args_list=problem_args_list)
@set_resource_limits(recursion_var='convergent_num', multiplier=1, set_int_max_str=True, when='always')
def sum_digits_numerator_nth_convergent_of_e(*, convergent_num: int) -> int:
    """Calculate the sum of digits in the numerator of the nth convergent of e.

    This function computes the nth convergent of the continued fraction expansion of e,
    extracts its numerator, and returns the sum of the digits in that numerator.

    The solution leverages the recursive nth_convergent_of_e function to generate the
    continued fraction convergent, and the utility function sum_digits to efficiently
    compute the digit sum.

    Args:
        convergent_num: The convergent number to calculate (1-indexed)

    Returns:
        The sum of digits in the numerator of the nth convergent

    Examples:
        >>> sum_digits_numerator_nth_convergent_of_e(convergent_num=10)
        17  # The numerator is 1457, and 1+4+5+7=17

        >>> sum_digits_numerator_nth_convergent_of_e(convergent_num=100)
        272  # The sum of digits in the numerator of the 100th convergent
    """
    return sum_digits(nth_convergent_of_e(convergent_num).numerator)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
