#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 949
# https://projecteuler.net/problem=949
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
solution to Project Euler problem 949
https://projecteuler.net/problem=949
Left and Right play a game with a number of words, each consisting of L's and R's, alternating turns. On Left's turn, for each word, Left can remove any number of letters (possibly zero), but not all the letters, from the left side of the word. However, at least one letter must be removed from at least one word. Right does the same on Right's turn except that Right removes letters from the right side of each word. The game continues until each word is reduced to a single letter. If there are more L's than R's remaining then Left wins; otherwise if there are more R's than L's then Right wins. In this problem we only consider games with an odd number of words, thus making ties impossible.

Let $G(n, k)$ be the number of ways of choosing $k$ words of length $n$, for which Right has a winning strategy when Left plays first. Different orderings of the same set of words are to be counted separately.

It can be seen that $G(2, 3)=14$ due to the following solutions (and their reorderings):
$$\begin{align}
(\texttt{LL},\texttt{RR},\texttt{RR})&:3\text{ orderings}\\
(\texttt{LR},\texttt{LR},\texttt{LR})&:1\text{ ordering}\\
(\texttt{LR},\texttt{LR},\texttt{RR})&:3\text{ orderings}\\
(\texttt{LR},\texttt{RR},\texttt{RR})&:3\text{ orderings}\\
(\texttt{RL},\texttt{RR},\texttt{RR})&:3\text{ orderings}\\
(\texttt{RR},\texttt{RR},\texttt{RR})&:1\text{ ordering}
\end{align}
$$You are also given $G(4, 3)=496$ and $G(8, 5)=26359197010$.

Find $G(20, 7)$ giving your answer modulo $1001001011$.

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