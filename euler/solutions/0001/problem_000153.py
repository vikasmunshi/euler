
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 153
# https://projecteuler.net/problem=153
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 153
    https://projecteuler.net/problem=153
    As we all know the equation $x^2=-1$ has no solutions for real $x$.


If we however introduce the imaginary number $i$ this equation has two solutions: $x=i$ and $x=-i$.


If we go a step further the equation $(x-3)^2=-4$ has two complex solutions: $x=3+2i$ and $x=3-2i$.

$x=3+2i$ and $x=3-2i$ are called each others' complex conjugate.


Numbers of the form $a+bi$ are called complex numbers.


In general $a+bi$ and $a-bi$ are each other's complex conjugate.
A Gaussian Integer is a complex number $a+bi$ such that both $a$ and $b$ are integers.


The regular integers are also Gaussian integers (with $b=0$).


To distinguish them from Gaussian integers with $b \ne 0$ we call such integers "rational integers."


A Gaussian integer $a+bi$ is called a divisor of a rational integer $n$ if the result $\dfrac n {a + bi}$ is also a Gaussian integer.


If for example we divide $5$ by $1+2i$ we can simplify $\dfrac{5}{1 + 2i}$ in the following manner:


Multiply numerator and denominator by the complex conjugate of $1+2i$: $1-2i$.


The result is $\dfrac{5}{1 + 2i} = \dfrac{5}{1 + 2i}\dfrac{1 - 2i}{1 - 2i} = \dfrac{5(1 - 2i)}{1 - (2i)^2} = \dfrac{5(1 - 2i)}{1 - (-4)} = \dfrac{5(1 - 2i)}{5} = 1 - 2i$.


So $1+2i$ is a divisor of $5$.


Note that $1+i$ is not a divisor of $5$ because $\dfrac{5}{1 + i} = \dfrac{5}{2} - \dfrac{5}{2}i$.


Note also that if the Gaussian Integer $(a+bi)$ is a divisor of a rational integer $n$, then its complex conjugate $(a-bi)$ is also a divisor of $n$.
In fact, $5$ has six divisors such that the real part is positive: $\{1, 1 + 2i, 1 - 2i, 2 + i, 2 - i, 5\}$.


The following is a table of all of the divisors for the first five positive rational integers:

$n$ Gaussian integer divisors

with positive real partSum $s(n)$ of 
these
divisors$1$$1$$1$
$2$$1, 1+i, 1-i, 2$$5$
$3$$1, 3$$4$
$4$$1, 1+i, 1-i, 2, 2+2i, 2-2i,4$$13$
$5$$1, 1+2i, 1-2i, 2+i, 2-i, 5$$12$
For divisors with positive real parts, then, we have: $\sum \limits_{n = 1}^{5} {s(n)} = 35$.
$\sum \limits_{n = 1}^{10^5} {s(n)} = 17924657155$.
What is $\sum \limits_{n = 1}^{10^8} {s(n)}$?

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
