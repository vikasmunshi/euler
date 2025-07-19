#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 85:

Problem Statement:
By counting carefully it can be seen that a rectangular grid measuring 3 by 2 contains eighteen rectangles:
    <see problem description at https://projecteuler.net/problem=85>
Although there exists no rectangular grid that contains exactly two million rectangles,
find the area of the grid with the nearest solution.

Solution Approach:
1. The number of rectangles in an m×n grid can be calculated as: sum[(m-i+1)(n-j+1)] for i=1..m, j=1..n
   This can be simplified to: (m(m+1)/2) * (n(n+1)/2)
2. We implement two approaches to find the grid with closest number of rectangles to the target:
   a. Brute force: Iterate through possible height and width combinations up to max_side
   b. Optimized: Use binary search to more efficiently find heights for each width
3. For each grid, we calculate the number of rectangles and track the grid dimensions
4. We return the area (height × width) of the grid whose rectangle count is closest to the target

Test Cases:
- Grid with exactly 18 rectangles: Answer = 6 (3×2 grid)
- Grid with closest to 2 million rectangles: Answer = 2772

URL: https://projecteuler.net/problem=85
Answer: 2772
"""
from bisect import bisect_left
from functools import partial
from itertools import product
from typing import Any, Dict, Tuple

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=85)
problem_number: int = 85

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'target_num_rectangles': 18, 'max_side': 10, 'max_error': 0}, answer=6, ),
    ProblemArgs(kwargs={'target_num_rectangles': 2 * 10 ** 6, 'max_side': 100, 'max_error': 2}, answer=2772, ),
]


def delta_func(kv: Tuple[int, Any], *, target_num: int) -> int:
    """Calculate the absolute difference between a value and the target number.

    Args:
        kv: A tuple where the first element is the number of rectangles
        target_num: The target number of rectangles

    Returns:
        The absolute difference between the number of rectangles and the target
    """
    return abs(kv[0] - target_num)


def num_rectangles(height: int, width: int) -> int:
    """Calculate the total number of rectangles in a grid with given dimensions.

    For a grid of height h and width w, a rectangle can be formed by selecting
    two points: top-left (i1, j1) and bottom-right (i2, j2) where:
    1 ≤ i1 ≤ i2 ≤ h and 1 ≤ j1 ≤ j2 ≤ w

    Args:
        height: The height of the grid
        width: The width of the grid

    Returns:
        The total number of rectangles that can be formed in the grid
    """
    return sum((height - h + 1) * (width - w + 1) for w in range(1, width + 1) for h in range(1, height + 1))


# Register this function as a solution for problem #85 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def grid_area_with_num_rectangles_all(*, target_num_rectangles: int, max_side: int, max_error: int) -> int:
    """Find the area of a grid with the number of rectangles closest to the target.

    This implementation uses a brute force approach by calculating the number of rectangles
    for each possible height and width combination up to max_side.

    Args:
        target_num_rectangles: The target number of rectangles to approximate
        max_side: The maximum length of any side of the grid to consider
        max_error: The maximum acceptable error between found and target rectangle count
                  (early termination condition)

    Returns:
        The area (height × width) of the grid with rectangle count closest to target
    """
    delta = partial(delta_func, target_num=target_num_rectangles)
    results: Dict[int, Tuple[int, int, int]] = {}
    for height, width in product(range(2, max_side), repeat=2):
        results[num := num_rectangles(height, width)] = height, width, height * width
        if delta((num, None)) <= max_error:
            break
    if show_solution():
        result = min(results.items(), key=delta)
        print(f'Grid with {result[0]} rectangles: {result[1]}')
    return min(results.items(), key=delta)[1][2]


def num_rectangles_along_axis(length: int) -> int:
    """Calculate the sum of possible rectangles along a single axis of length.

    This function computes the triangular number: length * (length + 1) / 2,
    which represents the number of subarrays possible in an array of given length.

    Args:
        length: The length of the axis

    Returns:
        The sum of rectangles along one dimension
    """
    return sum((length - num + 1) for num in range(1, length + 1))


# Register this function as a solution for problem #85 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def grid_area_with_num_rectangles_bisect(*, target_num_rectangles: int, max_side: int, max_error: int) -> int:
    """Find the area of a grid with the number of rectangles closest to the target.

    This implementation uses a more efficient approach with binary search to find
    the optimal height for each width, significantly reducing the search space.

    The formula for the number of rectangles in an m×n grid can be factored as:
    (m(m+1)/2) * (n(n+1)/2) where m is height and n is width.

    Args:
        target_num_rectangles: The target number of rectangles to approximate
        max_side: The maximum length of any side of the grid to consider
        max_error: The maximum acceptable error between found and target rectangle count
                  (early termination condition)

    Returns:
        The area (height × width) of the grid with rectangle count closest to target
    """
    delta = partial(delta_func, target_num=target_num_rectangles)
    results: Dict[int, Tuple[int, int, int]] = {}
    numbers: Tuple[int, ...] = tuple(num_rectangles_along_axis(length) for length in range(1, max_side))
    len_numbers = len(numbers)
    num: int = 0
    for width, num_width in enumerate(numbers, start=1):
        # Use binary search to find the best height for this width
        j = bisect_left(a=numbers, x=target_num_rectangles // num_width)
        # Check heights around the bisection point for best match
        for height in (j + 1, j + 2):
            if 0 <= (height - 1) < len_numbers:
                results[num := numbers[height - 1] * num_width] = height, width, height * width
        if delta((num, None)) <= max_error:
            break
    if show_solution():
        result = min(results.items(), key=delta)
        print(f'Grid with {result[0]} rectangles: {result[1]}')
    return min(results.items(), key=delta)[1][2]


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
