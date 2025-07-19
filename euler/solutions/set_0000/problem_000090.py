#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 90:

Problem Statement:
Each of the six faces on a cube has a different digit (0 to 9) written on it; the same is done to a second cube.
By placing the two cubes side-by-side in different positions we can form a variety of 2-digit numbers.

For example, the square number 64 could be formed:
 <see problem description at https://projecteuler.net/problem=90>

In fact, by carefully choosing the digits on both cubes it is possible to display all of the square numbers below
one-hundred: 01, 04, 09, 16, 25, 36, 49, 64, and 81.

For example, one way this can be achieved is by placing 0, 5, 6, 7, 8, 9 on one cube and 1, 2, 3, 4, 8, 9 on the other
cube.

However, for this problem we shall allow the 6 or 9 to be turned upside-down so that an arrangement like
0, 5, 6, 7, 8, 9 and 1, 2, 3, 4, 6, 7 allows for all nine square numbers to be displayed; otherwise it would be
impossible to obtain 09.

In determining a distinct arrangement we are interested in the digits on each cube, not the order.

• 1, 2, 3, 4, 5, 6 is equivalent to 3, 6, 4, 1, 2, 5
• 1, 2, 3, 4, 5, 6 is distinct from 1, 2, 3, 4, 5, 9

But because we are allowing 6 and 9 to be reversed, the two distinct sets in the last example both represent the
extended set 1, 2, 3, 4, 5, 6, 9 for the purpose of forming 2-digit numbers.

How many distinct arrangements of the two cubes allow for all of the square numbers to be displayed?

Solution Approach:
The solution generates all possible combinations of 6 digits (from 0-9) for each cube. For each pair of cubes,
we check if they can display all square numbers below 100. Since 6 and 9 can be flipped, they are treated as
interchangeable. We count all valid arrangements, considering that the order of digits on each cube doesn't matter,
but the pairing of cubes does.

Test Cases:
- Expected answer: 1217

URL: https://projecteuler.net/problem=90
Answer: 1217
"""
from itertools import combinations
from typing import List, Tuple

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=90)
problem_number: int = 90

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=1217),
]


# Register this function as a solution for problem #90 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def cube_digit_pairs() -> int:
    """Calculate the number of distinct arrangements of two cubes that can display all square numbers below 100.

    Returns:
        int: The number of valid cube arrangements
    """
    # Generate all perfect squares below 100 as two-digit numbers (with leading zeros)
    squares: List[Tuple[int, int]] = [(int((i_sq := f'{i * i:02d}')[0]), int(i_sq[1])) for i in range(1, 10)]

    # Check if a digit x can be displayed on a cube with digits d, considering 6/9 flipping
    def can_display(cube_digits: Tuple[int, ...], digit: int) -> bool:
        # Either the digit is directly on the cube, or it's a 6/9 and the cube has the other one
        return digit in cube_digits or (digit in [6, 9] and (6 in cube_digits or 9 in cube_digits))

    # Check if a pair of cubes can display all square numbers
    def can_pair_display_all(cube1: Tuple[int, ...], cube2: Tuple[int, ...]) -> bool:
        for first_digit, second_digit in squares:
            # Check if either cube1 shows first digit and cube2 shows second digit,
            # or cube1 shows second digit and cube2 shows first digit
            if not ((can_display(cube1, first_digit) and can_display(cube2, second_digit)) or
                    (can_display(cube1, second_digit) and can_display(cube2, first_digit))):
                return False
        return True

    # Generate all possible combinations of 6 digits from 0-9
    all_cubes: List[Tuple[int, ...]] = list(combinations(range(10), 6))
    cube_count: int = len(all_cubes)

    # Count all valid arrangements
    # Note: We only check pairs (i,j) where i≤j to avoid duplicates
    valid_arrangements: int = 0
    for i in range(cube_count):
        for j in range(i, cube_count):
            if can_pair_display_all(all_cubes[i], all_cubes[j]):
                valid_arrangements += 1

    return valid_arrangements


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
