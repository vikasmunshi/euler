#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 96:

Problem Statement:
Su Doku (Japanese meaning *number place*) is the name given to a popular puzzle concept. Its origin is unclear, but
credit must be attributed to Leonhard Euler who invented a similar, and much more difficult, puzzle idea called
Latin Squares. The objective of Su Doku puzzles, however, is to replace the blanks (or zeros) in a 9 by 9 grid in such
that each row, column, and 3 by 3 box contains each of the digits 1 to 9.  Below is an example of a typical starting
puzzle grid and its solution grid.
    <see problem description at https://projecteuler.net/problem=96>>
A well constructed Su Doku puzzle has a unique solution and can be solved by logic, although it may be necessary to
employ "guess and test" methods in order to eliminate options (there is much contested opinion over this).
The complexity of the search determines the difficulty of the puzzle; the example above is considered easy* because it
can be solved by straight forward direct deduction.

The 6K text file, sudoku.txt (right click and 'Save Link/Target As...'), contains fifty different Su Doku puzzles
ranging in difficulty, but all with unique solutions (the first puzzle in the file is the example above).

By solving all fifty puzzles find the sum of the 3-digit numbers found in the top left corner of each solution grid;
for example, 483 is the 3-digit number found in the top left corner of the solution grid above.

Solution Approach:
This solution implements a backtracking algorithm to solve Sudoku puzzles:
1. Parse the input file to extract all 50 Sudoku grids
2. For each grid, apply a recursive backtracking algorithm:
   - For each empty cell, find all possible valid numbers (1-9)
   - Try each possibility and recursively solve the rest of the grid
   - If a solution fails, backtrack and try the next possibility
3. Once all grids are solved, calculate the sum of the 3-digit numbers in the top-left corner of each solution

The implementation uses several helper functions:
- get_grids: Parses the input file and yields each 9x9 grid
- get_values_in_square: Finds all values in a 3x3 square containing a given cell
- get_possibilities: Determines valid numbers for an empty cell based on Sudoku rules
- fill_in: Recursive backtracking function that attempts to solve the grid
- print_grid: Visualizes the starting grid and its solution side by side

Test Cases:
- With the provided Sudoku file, the sum of all 3-digit numbers is 24702

URL: https://projecteuler.net/problem=96
Answer: 24702
"""
from copy import deepcopy
from typing import Generator, List

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.cached_requests import get_text_file

# The problem number from Project Euler (https://projecteuler.net/problem=96)
problem_number: int = 96

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'file_url': 'https://projecteuler.net/project/resources/p096_sudoku.txt'}, answer=24702, ),
]

# Type alias for a Sudoku grid: 9x9 grid of integers (0 represents empty cells)
Grid = List[List[int]]


def get_grids(file_url: str) -> Generator[Grid, None, None]:
    """Parse the Sudoku file and yield each 9x9 grid.

    Args:
        file_url: URL to the text file containing the Sudoku puzzles

    Yields:
        Grid: Each complete 9x9 Sudoku grid represented as a list of lists
    """
    grid: Grid = []
    for line in get_text_file(url=file_url).splitlines(keepends=False):
        if line.startswith('Grid'):
            grid = []
        else:
            grid.append([int(d) for d in line.strip()])
        if len(grid) == 9:
            yield grid


def get_values_in_square(grid: Grid, row: int, col: int) -> Generator[int, None, None]:
    """Get all values in the 3x3 square containing the given cell.

    Args:
        grid: The Sudoku grid
        row: Row index of the cell
        col: Column index of the cell

    Yields:
        int: Each value in the 3x3 square
    """
    row -= row % 3  # Find the top-left corner of the 3x3 square
    col -= col % 3
    for i in range(3):
        for j in range(3):
            yield grid[row + i][col + j]


def get_possibilities(grid: Grid, row: int, col: int) -> set[int]:
    """Find all possible valid numbers for a given empty cell.

    Determines valid numbers by checking Sudoku constraints:
    - No duplicate numbers in the same row
    - No duplicate numbers in the same column
    - No duplicate numbers in the same 3x3 square

    Args:
        grid: The Sudoku grid
        row: Row index of the cell
        col: Column index of the cell

    Returns:
        set[int]: Set of valid numbers (1-9) for the cell, or empty set if cell is already filled
    """
    if grid[row][col]:
        return set()
    possible = set(range(1, 10))
    for c in range(9):  # Remove numbers already in the same row
        possible.discard(grid[row][c])
    for r in range(9):  # Remove numbers already in the same column
        possible.discard(grid[r][col])
    for elem in get_values_in_square(grid, row, col):  # Remove numbers in same 3x3 square
        possible.discard(elem)
    return possible


def fill_in(grid: Grid, row: int, col: int) -> bool:
    """Recursively solve the Sudoku grid using backtracking.

    This function attempts to fill in the grid starting from the given position,
    and continues cell by cell, row by row. If it reaches a point where no valid
    number can be placed, it backtracks to try different possibilities.

    Args:
        grid: The Sudoku grid (modified in-place)
        row: Current row index
        col: Current column index

    Returns:
        bool: True if the grid was successfully solved, False if no solution exists
    """
    if row >= 9:  # Base case: reached the end of the grid
        return True
    if grid[row][col]:  # Skip cells that are already filled
        return fill_in(grid, row + 1 if col == 8 else row, (col + 1) % 9)
    possibilities = get_possibilities(grid, row, col)
    for possibility in possibilities:  # Try each possible number
        grid[row][col] = possibility
        if fill_in(grid, row + 1 if col == 8 else row, (col + 1) % 9):
            return True
        grid[row][col] = 0  # backtrack if this path doesn't lead to a solution
    return False


def print_grid(grid_0: Grid, grid_1: Grid) -> None:
    """Print two Sudoku grids side by side with box formatting.

    This function visualizes the original unsolved grid and the solved grid
    side by side with Unicode box-drawing characters, making it easy to compare
    the original puzzle with its solution.

    Args:
        grid_0: The first grid (typically the unsolved puzzle)
        grid_1: The second grid (typically the solved puzzle)
    """
    print('     Unsolved Grid       ⟶⟶⟶      Solved Grid        ')
    print('┌───────┬───────┬───────┐   ┌───────┬───────┬───────┐')
    for rb in range(3):  # Iterate through 3x3 blocks vertically
        if rb > 0:
            print('├───────┼───────┼───────┤   ├───────┼───────┼───────┤')
        for r in range(3):  # Iterate through rows within each block
            for cb in range(3):  # Iterate through 3x3 blocks horizontally (left grid)
                print('│', end='')
                for c in range(3):  # Iterate through columns within each block
                    print(' ', end='')
                    print(grid_0[rb * 3 + r][cb * 3 + c] or ' ', end='')
                print(' ', end='')
            print('│⟶⟶⟶' if rb == 1 and r == 1 else '│   ', end='')  # Arrow between grids
            for cb in range(3):  # Iterate through 3x3 blocks horizontally (right grid)
                print('│', end='')
                for c in range(3):  # Iterate through columns within each block
                    print(' ', end='')
                    print(grid_1[rb * 3 + r][cb * 3 + c] or ' ', end='')
                print(' ', end='')
            print('│ ')

    print('└───────┴───────┴───────┘   └───────┴───────┴───────┘')
    print(' ─────────────────────────────────────────────────── ')


# Register this function as a solution for problem #96 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def sudoku_solver(*, file_url: str) -> int:
    """Solve all Sudoku puzzles and sum the 3-digit numbers in their top-left corners.

    This is the main solution function that:
    1. Reads all Sudoku grids from the provided file URL
    2. Solves each grid using the backtracking algorithm
    3. Extracts the 3-digit number from the top-left corner (first 3 digits of first row)
    4. Sums these numbers across all solved puzzles
    5. Optionally displays the original and solved grids if show_solution() is True

    Args:
        file_url: URL to the text file containing the Sudoku puzzles

    Returns:
        int: Sum of all 3-digit numbers from the top-left corners of solved puzzles
    """
    s: int = 0
    if show_solution():  # Display mode with visualization
        for grid in get_grids(file_url=file_url):
            source_grid = deepcopy(grid)  # Keep original grid for display
            assert fill_in(grid, 0, 0), 'Failed to solve grid'
            s += int(''.join(map(str, grid[0][0:3])))  # Get 3-digit number from top-left
            print_grid(source_grid, grid)  # Display both grids side by side
    else:  # Silent mode for performance
        for grid in get_grids(file_url=file_url):
            assert fill_in(grid, 0, 0), 'Failed to solve grid'
            s += int(''.join(map(str, grid[0][0:3])))
    return s


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
