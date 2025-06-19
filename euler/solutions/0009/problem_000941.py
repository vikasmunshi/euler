
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 941
# https://projecteuler.net/problem=941
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 941
    https://projecteuler.net/problem=941
    
de Bruijn has a digital combination lock with $k$ buttons numbered $0$ to $k-1$ where $k \le 10$.

The lock opens when the last $n$ buttons pressed match the preset combination.


Unfortunately he has forgotten the combination. He creates a sequence of these digits which contains every possible combination of length $n$. Then by pressing the buttons in this order he is sure to open the lock.


Consider all sequences of shortest possible length that contains every possible combination of the digits.

Denote by $C(k, n)$ the lexicographically smallest of these.


For example, $C(3, 2) = $ 0010211220.


Define the sequence $a_n$ by $a_0=0$ and

$$a_n=(920461 a_{n-1}+800217387569)\bmod 10^{12} \text{ for }\  n > 0$$
Interpret each $a_n$ as a $12$-digit combination, adding leading zeros for any $a_n$ with less than $12$ digits.


Given a positive integer $N$, we are interested in the order the combinations $a_1,...,a_N$ appear in $C(10,12)$.

 Denote by $p_n$ the place, numbered $1,...,N$, in which $a_n$ appears out of $a_1,...,a_N$. Define $\displaystyle F(N)=\sum_{n=1}^Np_na_n$.


For example, the combination $a_1=800217387569$ is entered before $a_2=696996536878$. Therefore:
$$F(2)=1\cdot800217387569 + 2\cdot696996536878 = 2194210461325$$
You are also given $F(10)=32698850376317$.


Find $F(10^7)$. Give your answer modulo $1234567891$.



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
