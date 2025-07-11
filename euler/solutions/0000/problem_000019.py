# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 19: Counting Sundays

Problem Statement:
You are given the following information, but you may prefer to do some research for yourself.

* 1 Jan 1900 was a Monday.
* Thirty days has September, April, June and November.
* All the rest have thirty-one, saving February alone, which has twenty-eight, rain or shine.
* And on leap years, twenty-nine.
* A leap year occurs on any year evenly divisible by 4, but not on a century unless it is divisible by 400.

How many Sundays fell on the first of the month during the twentieth century (1 Jan 1901 to 31 Dec 2000)?

Solution Approach:
This problem tests our ability to handle calendar calculations, particularly with leap years and
day-of-week determination. We could implement our own calendar system from scratch (calculating
the day of the week using mathematical formulas like Zeller's Congruence), but Python's datetime
module provides all the functionality needed:

1. Library Utilization: We leverage Python's datetime module, which handles all the complex
   calendar rules, including leap years and day of week calculations.

2. Core Algorithm: We iterate through every month of every year in the specified range, checking
   if the first day of each month is a Sunday.

3. Implementation Details:
   - Create a date object for the first day of each month in the range
   - Check if the day of the week is Sunday (isoweekday() == 7)
   - Count the number of matches

By using built-in libraries, we avoid potential errors in leap year calculation and day-of-week
determination, making the solution both concise and robust.

The solution is elegant in its simplicity, using a comprehension to both generate the dates
and filter/count them in a single expression.

URL: https://projecteuler.net/problem=19
Answer: 171
"""
from datetime import date

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'start_year': 1901, 'end_year': 2000}, answer=171, ),
]


def sundays_on_first_of_month(*, start_year: int, end_year: int) -> int:
    """Count the number of Sundays that fall on the first day of the month in a given range of years.

    This function uses Python's datetime module to determine the day of the week for the
    first day of each month in the specified range of years. In the ISO calendar used by
    the datetime module, Monday is 1 and Sunday is 7.

    Implementation Details:
    1. We use a generator expression to create a sequence of all first-of-month dates
       within the specified year range.
    2. For each date, we check if it falls on a Sunday using the isoweekday() method.
    3. The sum() function counts all dates that satisfy the condition.

    The approach is concise and leverages Python's built-in libraries for date manipulation,
    avoiding the need to implement complex calendar calculations manually.

    Alternative Approaches:
    1. Manual Day-of-Week Calculation: One could implement Zeller's Congruence or similar
       formulas to determine the day of week without relying on the datetime module.
    2. Day Advancement: Starting from a known date (like 1 Jan 1900 = Monday), iteratively
       advance through all dates, tracking day of week and counting Sundays on the first.
    3. Calendar Module: Python's calendar module could also be used for similar functionality.

    Complexity Analysis:
    - Time Complexity: O(Y×M) where Y is the number of years and M is the number of months (12)
    - Space Complexity: O(1) as we only generate one date at a time in the generator expression

    Args:
        start_year: The first year to include in the count (inclusive)
        end_year: The last year to include in the count (inclusive)

    Returns:
        The count of Sundays that fall on the first day of any month in the range

    Example:
        >>> sundays_on_first_of_month(start_year=1901, end_year=2000)
        171  # There are 171 Sundays falling on the first of a month in the 20th century
    """
    return sum(date(y, m, day=1).isoweekday() == 7 for m in range(1, 13) for y in range(start_year, end_year + 1))


# Create an alias for the sundays_on_first_of_month function to match the expected solution interface
# This allows the function to be named descriptively while still conforming to the
# Project Euler framework's convention of using 'solution' as the entry point
solution = sundays_on_first_of_month

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
