# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 16: Power Digit Sum

Problem Statement:
2¹⁵ = 32768 and the sum of its digits is 3 + 2 + 7 + 6 + 8 = 26.
What is the sum of the digits of the number 2¹⁰⁰⁰?

Solution Approach:
This problem examines the behavior of digits in very large powers. The approach is straightforward
but relies on a programming language's ability to handle arbitrary-precision arithmetic:

1. Calculation of Large Number: We need to compute 2¹⁰⁰⁰, which is a 302-digit number that would
   cause overflow in languages with fixed-size integer types. Python naturally handles
   arbitrary-precision integers, making the calculation simple.

2. Digit Extraction: Once we have the large number, we convert it to a string and iterate
   through each character (digit) to compute the sum.

3. Generalization: While the original problem asks about 2¹⁰⁰⁰, our solution is generalized to
   handle any base and power, making it more versatile for similar problems.

The algorithm has a time complexity of O(log₁₀(base^power)), which is approximately
O(power·log₁₀(base)) - the number of digits in the result. The space complexity follows
the same pattern.

Python's ability to handle arbitrary-precision integers makes this problem trivial compared
to implementing it in languages that would require custom big integer libraries.

Test Cases:
- For power=15: Sum of digits in 2¹⁵ = 26
- For power=1000: Sum of digits in 2¹⁰⁰⁰ = 1366

URL: https://projecteuler.net/problem=16
Answer: 1366
"""
from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=16)
problem_number: int = 16

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'power': 15, 'base': 2}, answer=26, ),
    ProblemArgs(kwargs={'power': 1000, 'base': 2}, answer=1366, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def sum_of_digits(*, power: int, base: int) -> int:
    """Calculate the sum of digits in the number base^power.

    This function computes the sum of individual digits in the number resulting from
    raising 'base' to the power of 'power'. The solution leverages Python's built-in
    support for arbitrary-precision integers, which automatically handles large numbers
    without overflow issues.

    Implementation Details:
    1. Calculate base^power using Python's exponentiation operator (**)
    2. Convert the result to a string to access individual digits
    3. Iterate through each character, convert back to integer, and sum

    The algorithm's efficiency depends on Python's internal implementation of large
    integer arithmetic and string conversion, but is generally very fast even for
    large powers.

    Args:
        power: The exponent to which the base is raised
        base: The base number to be raised to the specified power (default: 2)

    Returns:
        The sum of all individual digits in the resulting number

    Complexity:
        Time: O(log₁₀(base^power)) - proportional to the number of digits
        Space: O(log₁₀(base^power)) - for storing the string representation

    Examples:
        >>> sum_of_digits(power=15)  # 2^15 = 32768
        26  # 3+2+7+6+8 = 26

        >>> sum_of_digits(power=10, base=10)  # 10^10 = 10,000,000,000
        1  # Only one non-zero digit: 1+0+...+0 = 1
    """
    return sum(int(i) for i in str(base ** power))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
