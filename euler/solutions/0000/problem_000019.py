#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 19 - Counting Sundays
# https://projecteuler.net/problem=19
# Answer: 171
# Notes: Leverages Python's datetime module for calendar calculations
import textwrap
from datetime import date
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'start_year': 1901, 'end_year': 2000},
        answer=171,
    ),
]


def sundays_on_first_of_month(*, start_year: int, end_year: int) -> int:
    """Count the number of Sundays that fall on the first day of the month in a given range of years.

    This function uses Python's datetime module to determine the day of the week for the
    first day of each month in the specified range of years. In the ISO calendar used by
    the datetime module, Monday is 1 and Sunday is 7.

    Args:
        start_year: The first year to include in the count (inclusive)
        end_year: The last year to include in the count (inclusive)

    Returns:
        The count of Sundays that fall on the first day of any month in the range
    """
    return sum(date(y, m, 1).isoweekday() == 7 for m in range(1, 13) for y in range(start_year, end_year + 1))


# Cast the function to SolutionProtocol to comply with the expected interface
# This allows us to use the function directly as our solution without wrapping it
solution = cast(SolutionProtocol, sundays_on_first_of_month)

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 19: Counting Sundays
https://projecteuler.net/problem=19

Problem Description:
You are given the following information, but you may prefer to do some research for yourself.
1 Jan 1900 was a Monday.
Thirty days has September,
April, June and November.
All the rest have thirty-one,
Saving February alone,
Which has twenty-eight, rain or shine.
And on leap years, twenty-nine.

A leap year occurs on any year evenly divisible by 4, but not on a century unless it is divisible by 400.

How many Sundays fell on the first of the month during the twentieth century (1 Jan 1901 to 31 Dec 2000)?

Solution Approach:
- Instead of implementing a complex calendar calculation algorithm from scratch,
  we leverage Python's built-in datetime module
- The datetime.date class automatically handles all calendar rules including leap years
- For each month in each year in the given range:
  - Create a date object for the first day of that month
  - Check if that day is a Sunday (isoweekday() == 7)
  - Count the number of matches
- This approach is simple, efficient, and avoids potential errors in calendar calculations


''').strip()

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
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
