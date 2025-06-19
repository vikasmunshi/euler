#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 353
# https://projecteuler.net/problem=353
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
solution to Project Euler problem 353
https://projecteuler.net/problem=353

A moon could be described by the sphere $C(r)$ with centre $(0,0,0)$ and radius $r$. 



There are stations on the moon at the points on the surface of $C(r)$ with integer coordinates. The station at $(0,0,r)$ is called North Pole station, the station at $(0,0,-r)$ is called South Pole station.



All stations are connected with each other via the shortest road on the great arc through the stations. A journey between two stations is risky. If d is the length of the road between two stations, $\left(\frac{d}{\pi r}\right)^2$ is a measure for the risk of the journey (let us call it the risk of the road). If the journey includes more than two stations, the risk of the journey is the sum of risks of the used roads.



A direct journey from  the North Pole station to the South Pole station has the length $\pi r$ and risk $1$. The journey from the North Pole station to the South Pole station via $(0,r,0)$ has the same length, but a smaller risk:
\[
\left(\frac{\frac{1}{2}\pi r}{\pi r}\right)^2+\left(\frac{\frac{1}{2}\pi r}{\pi r}\right)^2=0.5
\]


The minimal risk of a journey from the North Pole station to the South Pole station on $C(r)$ is $M(r)$.



You are given that $M(7)=0.1784943998$ rounded to $10$ digits behind the decimal point. 



Find $\displaystyle{\sum_{n=1}^{15}M(2^n-1)}$.



Give your answer rounded to $10$ digits behind the decimal point in the form a.bcdefghijk.




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