#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 58: Spiral Primes

Problem Statement:
Starting with 1 and spiralling anticlockwise in the following way, a square spiral with 
side length 7 is formed.
37 36 35 34 33 32 31
38 17 16 15 14 13 30
39 18  5  4  3 12 29
40 19  6  1  2 11 28
41 20  7  8  9 10 27
42 21 22 23 24 25 26
43 44 45 46 47 48 49

It is interesting to note that the odd squares lie along the bottom right diagonal, but 
what is more interesting is that 8 out of the 13 numbers lying along both diagonals are 
prime; that is, a ratio of 8/13 ≈ 62%.

If one complete new layer is wrapped around the spiral above, a square spiral with side 
length 9 will be formed. If this process is continued, what is the side length of the 
square spiral for which the ratio of primes along both diagonals first falls below 10%?

Solution Approach:
The solution uses a systematic approach to generate the diagonals of each spiral layer:

1. Pattern Recognition: In a square spiral, each layer adds a ring of numbers around the previous square.
   The corners of each layer can be calculated using a mathematical pattern.

2. Efficient Generation: Instead of building the entire spiral, we only calculate the corner values
   of each layer using a generator function that produces the side length and four corner values.

3. Prime Counting: For each new layer, we check if each corner is prime and keep track of the
   running ratio of primes to total diagonal elements.

4. Threshold Detection: We continue adding layers until the ratio falls below the specified threshold.

Test Cases:
- For threshold=0.10 (10%): The side length is 26,241

URL: https://projecteuler.net/problem=58
Answer: 26241
"""
from typing import Generator, Tuple
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol
from euler import primes

problem_args_list: ProblemArgsList = [ProblemArgs(kwargs={'threshold': 0.10}, answer=26241, ), ]


def generator_spiral_corners() -> Generator[Tuple[int, int, int, int, int], None, None]:
    """Generate the corners of each layer in a square number spiral.

    This generator function produces an infinite sequence of tuples, each representing
    a layer of the spiral with its side length and the four corner values. The spiral
    starts at 1 and grows outward anti-clockwise, with each layer adding a ring of
    numbers around the existing square.

    In the spiral pattern, the bottom right corners are always perfect squares (n²),
    and the other corners can be derived by subtracting multiples of (side length - 1)
    from this value.

    Returns:
        Generator yielding tuples with five integers:
            - side_length: The length of one side of the current square spiral layer
            - corner_bottom_right: The bottom right corner value (always n²)
            - corner_bottom_left: The bottom left corner value
            - corner_top_left: The top left corner value
            - corner_top_right: The top right corner value

    Example:
        The first yield is (3, 9, 7, 5, 3) representing the first layer with:
            - side length 3
            - corners 9 (bottom right), 7 (bottom left), 5 (top left), 3 (top right)

    Notes:
        - Layer 0 would be just the number 1 (not included in the yields)
        - Each layer adds a ring of numbers around the previous square
        - The generator continues indefinitely until stopped
    """
    layer = 0
    while layer := layer + 1:
        side_length = 2 * layer + 1
        side_length_min_1 = side_length - 1
        corner_bottom_right = side_length ** 2
        corner_bottom_left = corner_bottom_right - side_length_min_1
        corner_top_left = corner_bottom_left - side_length_min_1
        corner_top_right = corner_top_left - side_length_min_1
        yield side_length, corner_bottom_right, corner_bottom_left, corner_top_left, corner_top_right


def solution(*, threshold: float) -> int:
    """
    Find the side length of a square spiral where the ratio of primes on diagonals falls below a threshold.

    This solution generates each layer of a square spiral and counts the prime numbers
    on both diagonals. It continues until the ratio of primes to total diagonal elements
    falls below the specified threshold.

    Args:
        threshold: A float between 0 and 1 representing the percentage threshold
                   (e.g., 0.10 for 10%)

    Returns:
        The side length of the square spiral when the ratio first drops below the threshold

    Example:
        >>> solution(threshold=0.10)
        26241
    """
    # Initialize the prime number cache for faster primality testing
    primes.seed_cache()

    # Start with just the center element (1), which is not prime
    num_prime_diagonals: int = 0  # Count of prime numbers on the diagonals
    num_diagonal_elements: int = 1  # Total count of numbers on the diagonals (including 1)

    # Generate each layer of the spiral and check the corner values
    for side_length, corner_bottom_right, corner_bottom_left, corner_top_left, corner_top_right in generator_spiral_corners():
        # Each new layer adds 4 new diagonal elements
        num_diagonal_elements += 4

        # Check each corner for primality and update the count
        for corner in (corner_bottom_right, corner_bottom_left, corner_top_left, corner_top_right):
            num_prime_diagonals += primes.is_prime(corner)  # Adds 1 if prime, 0 if not

        # Calculate the current ratio and check against the threshold
        if num_prime_diagonals / num_diagonal_elements < threshold:
            return side_length
    else:
        # This should not happen, but included for completeness
        raise ValueError('No solution found')


if __name__ == '__main__':
    # This block is executed when the Python module is run directly.
    # It evaluates the solution function to ensure its correctness against test cases.

    # Importing required modules: `module_main` manages how the solution is invoked and tested,
    # while `cast` helps with type safety in passing the solution as a `SolutionProtocol`.
    from typing import cast
    from euler.evaluator import module_main

    # The `module_main` function handles the evaluation process by:
    # 1. Extracting the problem number from the file name for contextual usage.
    # 2. Accepting command-line arguments to configure execution, e.g., timeout or threading options.
    # 3. Running the `solution` function for all test cases defined in `problem_args_list`.
    # 4. Outputting the test results, including details such as whether the test passed/failed and time taken.
    # 5. Returning an appropriate exit code (exit code 0 indicates success, non-zero for failures).

    # The `SystemExit` ensures the program exits with the exit code returned by `module_main`.
    raise SystemExit(module_main(module_name=__file__,
                                 solution=cast(SolutionProtocol, solution),
                                 args_list=problem_args_list))
