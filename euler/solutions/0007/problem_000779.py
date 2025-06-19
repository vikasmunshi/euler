
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 779
# https://projecteuler.net/problem=779
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 779
    https://projecteuler.net/problem=779
    
For a positive integer $n \gt 1$, let $p(n)$ be the smallest prime dividing $n$, and let $\alpha(n)$ be its $p$-adic order, i.e. the largest integer such that $p(n)^{\alpha(n)}$ divides $n$.


For a positive integer $K$, define the function $f_K(n)$ by:
$$f_K(n)=\frac{\alpha(n)-1}{(p(n))^K}.$$

Also define $\overline{f_K}$ by:
$$\overline{f_K}=\lim_{N \to \infty} \frac{1}{N}\sum_{n=2}^{N} f_K(n).$$

It can be verified that $\overline{f_1} \approx 0.282419756159$.


Find $\displaystyle \sum_{K=1}^{\infty}\overline{f_K}$. Give your answer rounded to $12$ digits after the decimal point.



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
