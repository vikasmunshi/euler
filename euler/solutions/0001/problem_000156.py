
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 156
# https://projecteuler.net/problem=156
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 156
    https://projecteuler.net/problem=156
    Starting from zero the natural numbers are written down in base $10$ like this:


$0\,1\,2\,3\,4\,5\,6\,7\,8\,9\,10\,11\,12\cdots$

Consider the digit $d=1$. After we write down each number $n$, we will update the number of ones that have occurred and call this number $f(n,1)$. The first values for $f(n,1)$, then, are as follows:
\begin{array}{cc}
n & f(n, 1)\\
\hline
0 & 0\\
1 & 1\\
2 & 1\\
3 & 1\\
4 & 1\\
5 & 1\\
6 & 1\\
7 & 1\\
8 & 1\\
9 & 1\\
10 & 2\\
11 & 4\\
12 & 5
\end{array}

Note that $f(n,1)$ never equals $3$.


So the first two solutions of the equation $f(n,1)=n$ are $n=0$ and $n=1$. The next solution is $n=199981$.
In the same manner the function $f(n,d)$ gives the total number of digits $d$ that have been written down after the number $n$ has been written.


In fact, for every digit $d \ne 0$, $0$ is the first solution of the equation $f(n,d)=n$.
Let $s(d)$ be the sum of all the solutions for which $f(n,d)=n$.


You are given that $s(1)=22786974071$.
Find  $\sum s(d)$ for $1 \le d \le 9$.
Note: if, for some $n$, $f(n,d)=n$ for more than one value of $d$ this value of $n$ is counted again for every value of $d$ for which $f(n,d)=n$.

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
