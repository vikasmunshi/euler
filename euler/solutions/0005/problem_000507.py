
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 507
# https://projecteuler.net/problem=507
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 507
    https://projecteuler.net/problem=507
    
Let $t_n$ be the tribonacci numbers defined as:

$t_0 = t_1 = 0$;

$t_2 = 1$;

$t_n = t_{n-1} + t_{n-2} + t_{n-3}$ for $n \ge 3$

and let $r_n = t_n \text{ mod } 10^7$.


For each pair of Vectors $V_n=(v_1,v_2,v_3)$ and $W_n=(w_1,w_2,w_3)$ with $v_1=r_{12n-11}-r_{12n-10}, v_2=r_{12n-9}+r_{12n-8}, v_3=r_{12n-7} \cdot r_{12n-6}$  and 
 $w_1=r_{12n-5}-r_{12n-4}, w_2=r_{12n-3}+r_{12n-2}, w_3=r_{12n-1} \cdot r_{12n}$



we define $S(n)$ as the minimal value of the manhattan length of the vector $D=k \cdot V_n+l \cdot W_n$ measured as $|k \cdot v_1+l \cdot w_1|+|k \cdot v_2+l \cdot w_2|+|k \cdot v_3+l \cdot w_3|$
 for any integers $k$ and $l$ with $(k,l)\neq (0,0)$.

The first vector pair  is $(-1, 3, 28)$, $(-11, 125, 40826)$.

You are given that $S(1)=32$ and $\sum_{n=1}^{10} S(n)=130762273722$.


Find $\sum_{n=1}^{20000000} S(n)$.



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
