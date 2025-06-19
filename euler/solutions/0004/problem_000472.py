
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 472
# https://projecteuler.net/problem=472
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 472
    https://projecteuler.net/problem=472
    There are $N$ seats in a row. $N$ people come one after another to fill the seats according to the following rules:
No person sits beside another.
The first person chooses any seat.
Each subsequent person chooses the seat furthest from anyone else already seated, as long as it does not violate rule 1. If there is more than one choice satisfying this condition, then the person chooses the leftmost choice.
Note that due to rule 1, some seats will surely be left unoccupied, and the maximum number of people that can be seated is less than $N$ (for $N \gt 1$).

Here are the possible seating arrangements for $N = 15$:



We see that if the first person chooses correctly, the $15$ seats can seat up to $7$ people.

We can also see that the first person has $9$ choices to maximize the number of people that may be seated.

Let $f(N)$ be the number of choices the first person has to maximize the number of occupants for $N$ seats in a row. Thus, $f(1) = 1$, $f(15) = 9$, $f(20) = 6$, and $f(500) = 16$.

Also, $\sum f(N) = 83$ for $1 \le N \le 20$ and  $\sum f(N) = 13343$ for $1 \le N \le 500$.

Find $\sum f(N)$ for $1 \le N \le 10^{12}$. Give the last $8$ digits of your answer.


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
