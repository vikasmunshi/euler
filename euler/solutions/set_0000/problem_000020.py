# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 20: Factorial Digit Sum

Problem Statement:
n! means n × (n-1) × ... × 3 × 2 × 1

For example, 10! = 10 × 9 × ... × 3 × 2 × 1 = 3,628,800,
and the sum of the digits in the number 10! is 3 + 6 + 2 + 8 + 8 + 0 + 0 = 27.

Find the sum of the digits in the number 100!.

Solution Approach:
This problem combines two fundamental operations: factorial calculation and digit manipulation.

1. Factorial Calculation: We need to compute 100!, which is a massive number (158 digits long).
   This would cause overflow in languages with fixed-size integer types, but Python's built-in
   support for arbitrary-precision arithmetic handles this elegantly via the math.factorial function.

2. Digit Sum Calculation: Once we have the factorial value, we convert it to a string to easily
   access each digit, then sum the numeric values of these digits.

The beauty of this solution lies in its simplicity, leveraging Python's strengths:

- Arbitrary-precision integers that can handle extremely large numbers without overflow
- Easy conversion between numeric and string representations
- Functional programming features like generator expressions for concise digit summing

This approach is both efficient and readable. The factorial calculation has a time complexity
of O(n), and the digit sum calculation is O(log(n!)), which is approximately O(n log n) due
to the number of digits in n! growing logarithmically with the value of n!.

Test Cases:
- For n=10: Sum of digits in 10! = 27
- For n=100: Sum of digits in 100! = 648

URL: https://projecteuler.net/problem=20
Answer: 648
"""
from math import factorial

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=20)
problem_number: int = 20

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 10}, answer=27, ),
    ProblemArgs(kwargs={'n': 100}, answer=648, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def factorial_digit_sum(n: int) -> int:
    """Calculate the sum of digits in the factorial of a number.

    This function leverages Python's built-in factorial function from the math module,
    which can handle large integers. The resulting number is converted to a string
    to easily access and sum its individual digits.

    Implementation Details:
    1. Calculate n! using math.factorial(), which handles arbitrary-precision arithmetic
    2. Convert the result to a string representation
    3. Iterate through each character (digit), convert back to integer, and sum

    Python's ability to handle arbitrary-precision integers is crucial here, as factorial
    values grow extremely quickly. For example, 100! has 158 digits, far exceeding the
    capacity of fixed-size integer types in many programming languages.

    Complexity Analysis:
    - Time Complexity: O(n + d) where n is the input number (for factorial calculation)
      and d is the number of digits in n! (for the digit sum)
    - Space Complexity: O(d) for storing the string representation of the factorial

    Note that d, the number of digits in n!, grows approximately as O(n log n) according
    to Stirling's approximation, so the overall complexity is dominated by this term
    for large values of n.

    Args:
        n: A positive integer whose factorial's digits will be summed

    Returns:
        The sum of all digits in n!

    Examples:
        >>> factorial_digit_sum(10)  # 10! = 3,628,800
        27  # 3+6+2+8+8+0+0 = 27

        >>> factorial_digit_sum(5)  # 5! = 120
        3  # 1+2+0 = 3
    """
    return sum(int(d) for d in str(factorial(n)))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
