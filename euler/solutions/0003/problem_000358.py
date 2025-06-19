
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 358
# https://projecteuler.net/problem=358
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 358
    https://projecteuler.net/problem=358
    A cyclic number with $n$ digits has a very interesting property:

When it is multiplied by $1, 2, 3, 4, ..., n$, all the products have exactly the same digits, in the same order, but rotated in a circular fashion!



The smallest cyclic number is the $6$-digit number $142857$:

$142857 \times 1 = 142857$

$142857 \times 2 = 285714$

$142857 \times 3 = 428571$

$142857 \times 4 = 571428$

$142857 \times 5 = 714285$

$142857 \times 6 = 857142$



The next cyclic number is $0588235294117647$ with $16$ digits :

$0588235294117647 \times 1 = 0588235294117647$

$0588235294117647 \times 2 = 1176470588235294$

$0588235294117647 \times 3 = 1764705882352941$

$...$

$0588235294117647 \times 16 = 9411764705882352$



Note that for cyclic numbers, leading zeros are important.



There is only one cyclic number for which, the eleven leftmost digits are $00000000137$ and the five rightmost digits are $56789$ (i.e., it has the form $00000000137 \cdots 56789$ with an unknown number of digits in the middle). Find the sum of all its digits.



    """
    raise NotImplementedError


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
