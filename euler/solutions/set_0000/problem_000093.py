#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 93:

Problem Statement:
By using each of the digits from the set, 1, 2, 3, 4, exactly once, and making use of the four arithmetic operations
(+, -, ×, /) and brackets/parentheses, it is possible to form different positive integer targets.

For example,

8 = (4 × (1 + 3)) / 2
14 = 4 × (3 + 1 / 2)
19 = 4 × (2 + 3) - 1
36 = 3 × 4 × (2 + 1)

Note that concatenations of the digits, like 12 + 34, are not allowed.

Using the set, 1, 2, 3, 4, it is possible to obtain thirty-one different target numbers of which 36 is the maximum, and
each of the numbers 1 to 28 can be obtained before encountering the first non-expressible number.

Find the set of four distinct digits, a < b < c < d, for which the longest set of consecutive positive integers, 1 to n,
can be obtained, giving your answer as a string: *abcd*.

Solution Approach:
This solution explores all possible combinations of four distinct digits (a < b < c < d), where each digit is
between 1 and 9. For each combination:
1. We generate all possible values that can be obtained by applying the four arithmetic operations (+, -, ×, /) to these
   digits in all possible orders and with all possible parentheses arrangements.
2. We then find the length of the longest consecutive sequence of positive integers starting from 1.
3. The digit combination that produces the longest sequence is our answer, returned as a string "abcd".

The core of the solution uses recursive evaluation of all possible expressions that can be formed with the given digits.
For each pair of numbers, we apply all operations and recursively process the remaining numbers with the result.

Test Cases:
Given in the problem: Using digits 1, 2, 3, 4, we can obtain all integers from 1 to 28.
Expected Answer: 1258

URL: https://projecteuler.net/problem=93
Answer: 1258
"""
from functools import lru_cache  # For memoization to optimize recursive function calls
from typing import Set, Tuple  # Type hints for function signatures

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=93)
problem_number: int = 93

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [ProblemArgs(kwargs={}, answer='1258', ), ]


@lru_cache(maxsize=None)
def eval_all_operations(vals: Tuple[int | float, ...]) -> Set[int | float]:
    """
    Recursively evaluates all possible outcomes for arithmetic operations on a given sequence of numbers.

    This function explores all possible ways to combine the numbers in the sequence using
    addition, subtraction, multiplication, and division operations. It recursively processes
    each pair of numbers, applies all operations, and continues with the remaining numbers.

    Parameters:
        vals (Tuple[int | float, ...]): A tuple of numbers (integers or floats) to evaluate.
             Uses tuple instead of Sequence for lru_cache compatibility.

    Returns:
        Set[int | float]: A set of integers or floats representing all possible results of arithmetic operations
                  that can be obtained using the input numbers.

    Notes:
        - Uses recursion to evaluate all possible combinations of operations
        - Employs lru_cache for memoization to avoid recalculating the same inputs
        - Handles base case when only one number remains
        - Avoids division by zero by checking divisor values
        - Uses absolute value for subtraction to ensure all possible outcomes
    """
    if (len_v := len(vals)) == 1:
        return {vals[0]}
    s = set()
    for i in range(len_v - 1):
        for j in range(i + 1, len_v):
            a, b = vals[i], vals[j]
            r = tuple([vals[k] for k in range(len_v) if k not in (i, j)])
            s |= eval_all_operations(r + (a + b,))  # Addition
            s |= eval_all_operations(r + (abs(a - b),))  # Subtraction (absolute value)
            s |= eval_all_operations(r + (a * b,))  # Multiplication
            if b > 0:  # Division (a/b)
                s |= eval_all_operations(r + (a / b,))
            if a > 0:  # Division (b/a)
                s |= eval_all_operations(r + (b / a,))
    return s


# Register this function as a solution for problem #93 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def arithmetic_expressions() -> str:
    """
    Finds the set of four distinct digits (a < b < c < d) that produces the longest sequence of
    consecutive positive integers starting from 1 using arithmetic operations.

    This function iterates through all possible combinations of four distinct single digits (1-9),
    ensuring they are in ascending order. For each combination, it:
    1. Calculates all possible integer values that can be obtained using the four arithmetic operations
    2. Finds the longest consecutive sequence of positive integers starting from 1
    3. Tracks the combination that yields the longest sequence

    Returns:
        str: A string concatenation of the four digits (abcd) that produces the longest
             consecutive sequence of integers starting from 1.

    Performance Optimization:
        - Uses memoization via lru_cache to avoid recalculating identical expressions
        - Prints cache statistics at the end of execution to show cache effectiveness
        - Converts lists to tuples for hashability to work with the cache

    Time Complexity:
        O(9^4) for digit combinations, with significant optimization through memoization
    """
    max_digits: str = ''
    max_length: int = 0
    max_results: Set[int] = set()

    # Iterate over all combinations of 4 distinct digits in ascending order
    for a in range(1, 7):
        for b in range(a + 1, 8):
            for c in range(b + 1, 9):
                for d in range(c + 1, 10):
                    # Get all possible integer results for this digit combination
                    results: Set[int] = {int(x) for x in eval_all_operations((a, b, c, d)) if x.is_integer()}

                    # Find the length of consecutive integers starting from 1
                    length = 0
                    while length + 1 in results:
                        length += 1

                    # Update if this combination produces a longer sequence
                    if length > max_length:
                        max_length, max_digits, max_results = length, f'{a}{b}{c}{d}', results

    # Optionally display detailed results for debugging/verification
    if show_solution():
        print(f'{max_digits=} {max_length=} {max_results=}')

    return max_digits


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
