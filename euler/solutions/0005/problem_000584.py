#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 584
# https://projecteuler.net/problem=584
# Answer: 
# Notes: 
import textwrap
from typing import Any, Dict

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(**kwarg: Dict[str, Any]) -> SolutionResult:
    # enter the solution here
    raise NotImplementedError


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 584
https://projecteuler.net/problem=584
A long long time ago in a galaxy far far away, the Wimwians, inhabitants of planet WimWi, discovered an unmanned drone that had landed on their planet. On examining the drone, they uncovered a device that sought the answer for the so called "Birthday Problem". The description of the problem was as follows:

If people on your planet were to enter a very large room one by one, what will be the expected number of people in the room when you first find 3 people with Birthdays within 1 day from each other.

The description further instructed them to enter the answer into the device and send the drone into space again. Startled by this turn of events, the Wimwians consulted their best mathematicians. Each year on Wimwi has 10 days and the mathematicians assumed equally likely birthdays and ignored leap years (leap years in Wimwi have 11 days), and found 5.78688636 to be the required answer. As such, the Wimwians entered this answer and sent the drone back into space.


After traveling light years away, the drone then landed on planet Joka. The same events ensued except this time, the numbers in the device had changed due to some unknown technical issues. The description read:

If people on your planet were to enter a very large room one by one, what will be the expected number of people in the room when you first find 3 people with Birthdays within 7 days from each other.

With a 100-day year on the planet, the Jokars (inhabitants of Joka) found the answer to be 8.48967364 (rounded to 8 decimal places because the device allowed only 8 places after the decimal point) assuming equally likely birthdays. They too entered the answer into the device and launched the drone into space again.


This time the drone landed on planet Earth. As before the numbers in the problem description had changed. It read:

If people on your planet were to enter a very large room one by one, what will be the expected number of people in the room when you first find 4 people with Birthdays within 7 days from each other.

What would be the answer (rounded to eight places after the decimal point) the people of Earth have to enter into the device for a year with 365 days? Ignore leap years. Also assume that all birthdays are equally likely and independent of each other.

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