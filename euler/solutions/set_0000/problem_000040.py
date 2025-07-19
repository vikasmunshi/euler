#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 40: Champernowne's constant

Problem Statement:
An irrational decimal fraction is created by concatenating the positive integers:
0.123456789101112131415161718192021...

It can be seen that the 12th digit of the fractional part is 1.

If d_n represents the nth digit of the fractional part, find the value of the following expression:
d_1 × d_10 × d_100 × d_1000 × d_10000 × d_100000 × d_1000000

Solution Approach:
This solution efficiently calculates the digits at specific positions in Champernowne's constant
without generating the entire sequence. The approach uses mathematical patterns to determine:
1. Which number in the sequence contains the desired position
2. Which digit within that number corresponds to the position

The algorithm avoids generating the entire constant by calculating ranges of positions
for numbers with the same number of digits, then locating the specific number and digit
through offset calculations.

Test Cases:
- d_1 = 1
- d_10 = 1
- d_100 = 5
- d_1000 = 3
- d_10000 = 7
- d_100000 = 2
- d_1000000 = 1

URL: https://projecteuler.net/problem=40
Answer: 210
"""
from functools import reduce

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=40)
problem_number: int = 40

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'i': 1}, answer=1, ),
    ProblemArgs(kwargs={'i': 2}, answer=5, ),
    ProblemArgs(kwargs={'i': 3}, answer=15, ),
    ProblemArgs(kwargs={'i': 4}, answer=105, ),
    ProblemArgs(kwargs={'i': 5}, answer=210, ),
    ProblemArgs(kwargs={'i': 6}, answer=210, ),
    ProblemArgs(kwargs={'i': 7}, answer=1470, ),
    ProblemArgs(kwargs={'i': 8}, answer=11760, ),
    ProblemArgs(kwargs={'i': 9}, answer=11760, ),
    ProblemArgs(kwargs={'i': 10}, answer=11760, ),
    ProblemArgs(kwargs={'i': 11}, answer=0, ),
]


def get_nth_digit_champernowne_s_constant(n: int) -> int:
    """
    Calculate the nth digit of Champernowne's constant.

    This helper function efficiently determines which digit appears at the
    specified position in Champernowne's constant without generating the entire sequence.

    Args:
        n: The position of the digit to find (1-indexed)

    Returns:
        The digit at the nth position as an integer

    Example:
        >>> get_nth_digit_champernowne_s_constant(12)
        1  # The 12th digit in the sequence is 1
        >>> get_nth_digit_champernowne_s_constant(1)
        1  # The 1st digit is 1
        >>> get_nth_digit_champernowne_s_constant(10)
        1  # The 10th digit is 1 (from the number 10)
    """
    length_till_num_digits, length_with_num_digits, num_digits = 0, 0, 0
    while length_with_num_digits < n:
        num_digits += 1
        length_till_num_digits = length_with_num_digits
        length_with_num_digits += num_digits * 9 * 10 ** (num_digits - 1)

    offset_of_number = n - length_till_num_digits - 1
    digit_in_number = offset_of_number % num_digits
    number = 10 ** (num_digits - 1) + offset_of_number // num_digits
    return int(str(number)[digit_in_number])


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def product_specific_digits_champernowne_constant(*, i: int) -> int:
    """
    Calculate the product of specific digits in Champernowne's constant.

    This solution finds the product of digits at positions 10^0, 10^1, 10^2, ..., 10^i
    in Champernowne's constant (0.123456789101112...) without generating the
    entire sequence. It uses efficient position calculations to find each digit.

    Args:
        i: The maximum exponent to consider (inclusive).
           For the original problem, i=6 to get positions 1, 10, 100, ..., 1,000,000

    Returns:
        The product of the digits at the specified positions

    Example:
        >>> product_specific_digits_champernowne_constant(i=6)
        210  # Product of digits at positions 1, 10, 100, 1000, 10000, 100000, 1000000
        >>> product_specific_digits_champernowne_constant(i=2)
        5    # Product of digits at positions 1, 10, 100
    """
    return reduce(lambda x, y: x * y, (get_nth_digit_champernowne_s_constant(10 ** i) for i in range(0, i + 1)), 1)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
