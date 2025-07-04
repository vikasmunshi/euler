# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 58
# https://projecteuler.net/problem=58
# Answer: 26241
# Notes:
"""
Solution to Project Euler problem 58: Spiral primes.

This module finds the side length of a square spiral for which the ratio of prime numbers
along both diagonals first falls below a given threshold (10% in the original problem).

The square spiral is formed by starting with 1 and spiraling outward in an anti-clockwise
direction. Each new layer adds a ring of numbers around the existing square, and we track
the corner values on both diagonals to calculate the ratio of primes.

Key concepts:
- Number spirals and their mathematical properties
- Primality testing
- Spiral pattern generation
- Ratio calculation with progressive sampling

The solution works by:
1. Generating each layer of the spiral, calculating the four corners
2. Testing each corner for primality
3. Tracking the ratio of primes to total diagonal elements
4. Returning the side length when the ratio falls below the threshold
"""
from typing import cast, Generator, Tuple

from euler import primes
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Test case for the problem: find side length when ratio of primes falls below 10%
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
    r"""
    Find the side length of a square spiral where the ratio of primes on diagonals falls below a threshold.

    This function calculates when the ratio of prime numbers along both diagonals of a
    square number spiral first falls below the given threshold. The spiral starts with 1
    at the center and grows outward in an anti-clockwise pattern.

    For example, with a 7×7 spiral:
    37 36 35 34 33 32 31
    38 17 16 15 14 13 30
    39 18  5  4  3 12 29
    40 19  6  1  2 11 28
    41 20  7  8  9 10 27
    42 21 22 23 24 25 26
    43 44 45 46 47 48 49

    The diagonal numbers are: 1, 3, 5, 7, 9, 13, 17, 21, 25, 31, 37, 43, 49
    Of these, 8 are prime (3, 5, 7, 13, 17, 31, 37, 43), giving a ratio of 8/13 ≈ 62%.

    Args:
        threshold: A float between 0 and 1 representing the percentage threshold
                   (e.g., 0.10 for 10%)

    Returns:
        The side length of the square spiral when the ratio first drops below the threshold

    Raises:
        ValueError: If no solution is found (should not occur for this problem)

    Notes:
        - The solution initializes the prime number cache for efficient primality testing
        - The center value (1) is counted as a diagonal element but not as a prime
    """
    # Initialize the prime number cache for faster primality testing
    primes.seed_cache()

    # Start with just the center element (1), which is not prime
    num_prime_diagonals: int = 0    # Count of prime numbers on the diagonals
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
    # When run directly, evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments
    args = parser.parse_args()

    # Set the logging level based on command-line arguments
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers
    evaluate_solution(solution=cast(SolutionProtocol, solution), args_list=problem_args_list, timeout=timeout,
                      max_workers=max_workers)
