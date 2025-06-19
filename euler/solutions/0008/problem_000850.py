
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 850
# https://projecteuler.net/problem=850
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 850
    https://projecteuler.net/problem=850
    Any positive real number $x$ can be decomposed into integer and fractional parts $\lfloor x \rfloor + \{x\}$, where $\lfloor x \rfloor$ (the floor function) is an integer, and $0\le \{x\} < 1$.

For positive integers $k$ and $n$, define the function
\begin{align}
f_k(n) = \sum_{i=1}^{n}\left\{ \frac{i^k}{n} \right\}
\end{align}
For example, $f_5(10)=4.5$ and $f_7(1234)=616.5$.

Let
\begin{align}
S(N) = \sum_{\substack{k=1 \\ k\text{ odd}}}^{N} \sum_{n=1}^{N}  f_k(n)
\end{align}
You are given that $S(10)=100.5$ and $S(10^3)=123687804$.

Find $\lfloor S(33557799775533) \rfloor$. Give your answer modulo 977676779.


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
