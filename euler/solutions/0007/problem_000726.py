
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 726
# https://projecteuler.net/problem=726
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 726
    https://projecteuler.net/problem=726
    
Consider a stack of bottles of wine. There are $n$ layers in the stack with the top layer containing only one bottle and the bottom layer containing $n$ bottles. For $n=4$ the stack looks like the picture below.




The collapsing process happens every time a bottle is taken. A space is created in the stack and that space is filled according to the following recursive steps:

No bottle touching from above: nothing happens. For example, taking $F$.
One bottle touching from above: that will drop down to fill the space creating another space. For example, taking $D$.
Two bottles touching from above: one will drop down to fill the space creating another space. For example, taking $C$.


This process happens recursively; for example, taking bottle $A$ in the diagram above. Its place can be filled with either $B$ or $C$. If it is filled with $C$ then the space that $C$ creates can be filled with $D$ or $E$. So there are 3 different collapsing processes that can happen if $A$ is taken, although the final shape (in this case) is the same.


Define $f(n)$ to be the number of ways that we can take all the bottles from a stack with $n$ layers. 
Two ways are considered different if at any step we took a different bottle or the collapsing process went differently.


You are given $f(1) = 1$, $f(2) = 6$ and $f(3) = 1008$.


Also define
$$S(n) = \sum_{k=1}^n f(k).$$

Find $S(10^4)$ and give your answer modulo $1\,000\,000\,033$.


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
