#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 56: Powerful Digit Sum

Problem Statement:
A googol (10^100) is a massive number: one followed by one-hundred zeros; 100^100 is almost
unimaginably large: one followed by two-hundred zeros. Despite their size, the sum of the
digits in each number is only 1.

Considering natural numbers of the form a^b, where a, b < 100, what is the maximum digital sum?

Solution Approach:
This solution explores all combinations of a^b where a and b are below a given limit (determined by
num_digits parameter). For efficiency, the solution focuses on larger values of a and b where higher
digital sums are more likely to be found.

The implementation includes two modes:
1. Standard mode: Efficiently calculates the maximum digital sum without visualization
2. Visualization mode: When the VISUALIZE environment variable is set, generates heatmaps
   showing digital sums, digit lengths, and average digit values

Test Cases:
- For num_digits=1 (a,b < 10): 45
- For num_digits=2 (a,b < 100): 972 (original problem)
- For num_digits=3 (a,b < 1000): 13,888
- For num_digits=4 (a,b < 10000): 181,855

URL: https://projecteuler.net/problem=56
Answer: 972
"""

from typing import Tuple

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.sys_utils import set_resource_limits
from euler.types import ProblemArgs, ProblemArgsList

matplotlib.use('TkAgg')  # Set the backend for non-interactive plotting
# The problem number from Project Euler (https://projecteuler.net/problem=56)
problem_number: int = 56

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'num_digits': 1}, answer=45, ),  # For a,b < 10
    ProblemArgs(kwargs={'num_digits': 2}, answer=972, ),  # For a,b < 100 (original problem)
    ProblemArgs(kwargs={'num_digits': 3}, answer=13888, ),  # For a,b < 1000
    # ProblemArgs(kwargs={'num_digits': 4}, answer=181855, ),  # For a,b < 10000
    # ProblemArgs(kwargs={'num_digits': 5}, answer=2257048, ),  # Commented out for performance
]


def visualize(data_matrix: np.ndarray[Tuple[int, int], np.uint64],  # type: ignore[type-var]
              len_matrix: np.ndarray[Tuple[int, int], np.float64],  # type: ignore[type-var]
              avg_matrix: np.ndarray[Tuple[int, int], np.float64],  # type: ignore[type-var]
              *, num_digits: int, stop_at: int, start_at: int) -> None:
    """
    Visualize three heatmaps side by side showing digital sum, digit length, and average digit value.

    This function creates a visualization of three related metrics for base^exponent calculations:
    1. Digital Sum: Sum of all digits in the number
    2. Length: Number of digits in the number
    3. Average Digit Value: Average value of all digits in the number

    The function automatically identifies the maximum digital sum and highlights its coordinates
    across all three heatmaps for easy comparison.

    Parameters:
    -----------
    data_matrix : np.ndarray[Tuple[int, int], np.uint64]
        2D array containing the digital sum for each base^exponent combination
    len_matrix : np.ndarray[Tuple[int, int], np.float64]
        2D array containing the number of digits for each base^exponent combination
    avg_matrix : np.ndarray[Tuple[int, int], np.float64]
        2D array containing the average digit value for each base^exponent combination
    num_digits : int
        Number of digits in the problem constraint (e.g., 2 for a,b < 100)
    stop_at : int
        Upper bound for visualization (exclusive)
    start_at : int
        Lower bound for visualization (inclusive)

    Returns:
    --------
    None
        Displays the visualization but does not return any value
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

    # Plot digital sum heatmap
    cmap = matplotlib.colormaps['YlOrRd'].copy()
    cmap.set_under(cmap(0.0))
    max_value = int(data_matrix.max())
    row_indices, col_indices = max_coords = np.where(data_matrix == max_value)
    len_value = len_matrix[row_indices[0], col_indices[0]]  # type: ignore[call-overload]
    avg_value = avg_matrix[row_indices[0], col_indices[0]]  # type: ignore[call-overload]
    base, exp = max_coords[0][0] + start_at, max_coords[1][0] + start_at
    cmap.set_over('black')
    plt.sca(ax1)
    cax1 = ax1.imshow(data_matrix, cmap=cmap, aspect='equal', origin='lower',
                      extent=(start_at, stop_at, start_at, stop_at), vmin=0, vmax=max_value - 1)
    colorbar1 = plt.colorbar(cax1, ax=ax1, label='Digital Sum')
    max_info = f'{max_value=} at base={int(base)}, exp={int(exp)}'
    ax1.set_title(f'Digital Sum for {num_digits=}\n({max_info})')
    ax1.set_xlabel('Exponent')
    ax1.set_ylabel('Base')
    ax1.format_coord = lambda x, y: f'base={int(y)}, exponent={int(x)}'
    cax1.format_cursor_data = lambda data: f'digital sum={int(data)}'
    ax1.grid(visible=False, which='both')

    # Plot Length digit heatmap
    plt.sca(ax2)
    cax2 = ax2.imshow(len_matrix, cmap=cmap, aspect='equal', origin='lower',
                      extent=(start_at, stop_at, start_at, stop_at))
    colorbar2 = plt.colorbar(cax2, ax=ax2, label='Length Digits')
    max_info = f'value at base={int(base)}, exp={int(exp)} is {len_value:.0f} digits long'
    ax2.set_title(f'Length Digital Sum for {num_digits=}\n({max_info})')
    ax2.set_xlabel('Exponent')
    ax2.set_ylabel('Base')
    ax2.format_coord = lambda x, y: f'base={int(y)}, exponent={int(x)}'
    cax2.format_cursor_data = lambda data: f'len digits={data}'
    ax2.grid(visible=False, which='both')

    # Plot Average digit heatmap
    plt.sca(ax3)
    cax3 = ax3.imshow(avg_matrix, cmap=cmap, aspect='equal', origin='lower',
                      extent=(start_at, stop_at, start_at, stop_at))
    colorbar3 = plt.colorbar(cax3, ax=ax3, label='Average Digit Value')
    max_info = f'value at base={int(base)}, exp={int(exp)} has {avg_value} average digit value'
    ax3.set_title(f'Average Digit Value for {num_digits=}\n({max_info})')
    ax3.set_xlabel('Exponent')
    ax3.set_ylabel('Base')
    ax3.format_coord = lambda x, y: f'base={int(y)}, exponent={int(x)}'
    cax3.format_cursor_data = lambda data: f'avg digit={data:.1f}'
    ax3.grid(visible=False, which='both')

    for axis in (colorbar1.ax.xaxis, colorbar1.ax.yaxis,
                 colorbar2.ax.xaxis, colorbar2.ax.yaxis,
                 colorbar3.ax.xaxis, colorbar3.ax.yaxis):
        axis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins='auto', integer=True, min_n_ticks=1, prune='both'))
        axis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%d'))
        axis.set_ticks_position('both')

    plt.tight_layout()
    plt.show()


@register_solution(problem_number=problem_number, args_list=problem_args_list)
@set_resource_limits(set_int_max_str=True, when='always')
def max_digital_sum_of_exponent_numbers(*, num_digits: int) -> int:
    """
    Find the maximum digital sum of numbers of the form a^b where a,b < 10^num_digits.

    This function calculates the maximum possible sum of digits in numbers of the form a^b,
    where both a and b are less than 10^num_digits. For example, when num_digits=2, we
    consider all combinations where a,b < 100, which is the original Project Euler problem.

    The function operates in two modes:
    1. Standard mode: Efficiently calculates the maximum digital sum without visualization
    2. Visualization mode: When VISUALIZE environment variable is set, generates heatmaps
       showing digital sums, digit lengths, and average digit values

    Parameters:
    -----------
    num_digits : int
        Number of digits in the constraint, affecting the upper bound of calculation
        (e.g., num_digits=2 means a,b < 100)

    Returns:
    --------
    int
        The maximum digital sum found among all a^b combinations within the constraints

    Notes:
    ------
    - Sets sys.set_int_max_str_digits(0) to remove Python's string conversion limits
    - For optimization, does not calculate all possible combinations but focuses on
      larger values near the upper bound where larger sums are more likely
    - When VISUALIZE env var is set, creates three heatmaps showing digital sums,
      digit lengths, and average digit values
    """

    # Upper bound for bases and exponents based on num_digits (e.g., 100 for num_digits=2)
    stop_at: int = 10 ** num_digits

    # Standard calculation mode (no visualization)
    if not show_solution():
        # Optimization: Only check larger values where higher digital sums are likely
        # This significantly reduces computation time for large num_digits values
        return max([sum([int(d) for d in str(base ** exp)])
                    for base in range(max(1, stop_at - 100), stop_at)
                    for exp in range(max(1, stop_at - 10), stop_at)])

    # Visualization mode - activated when VISUALIZE environment variable is set
    else:
        # Set lower bound for calculation, focusing on larger numbers
        start_at: int = max(1, stop_at - 100)

        # Create matrix to store digital sums for each base^exponent combination
        data_matrix: np.ndarray[Tuple[int, int], np.uint64] = (  # type: ignore[type-var]
            np.zeros(shape=(stop_at - start_at, stop_at - start_at), dtype=np.uint64))

        # Calculate digital sum for each base^exponent combination
        for base, exp in ((base, exp) for base in range(start_at, stop_at) for exp in range(start_at, stop_at)):
            num = base ** exp
            num_str = str(num)
            data_matrix[base - start_at, exp - start_at] = sum(int(d) for d in num_str)

        # Calculate digit length for each value using vectorized operations for efficiency
        vectorized_len = np.vectorize(lambda value: len(str(value)))
        len_matrix = vectorized_len(data_matrix)

        # Calculate average digit value for each base^exponent combination
        vectorized_avg = np.vectorize(lambda value, length: sum([int(d) for d in str(value)]) / length)
        avg_matrix = vectorized_avg(data_matrix, len_matrix)

        # Print diagnostic information about the matrices
        print(data_matrix)  # Matrix of digital sums
        print(f'{data_matrix.shape=}')  # Shape of the matrix (rows, columns)
        print(len_matrix)  # Matrix of digit lengths
        print(f'{len_matrix.shape=}')  # Should match data_matrix.shape
        print(avg_matrix)  # Matrix of average digit values
        print(f'{avg_matrix.shape=}')  # Should match data_matrix.shape
        print(f'{avg_matrix.max()=}')  # Maximum average digit value

        # Generate the visualization with all three heatmaps
        visualize(data_matrix=data_matrix, len_matrix=len_matrix, avg_matrix=avg_matrix,
                  num_digits=num_digits, stop_at=stop_at, start_at=start_at)

        # Return the maximum digital sum found
        return int(data_matrix.max())


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
