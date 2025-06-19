#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from euler.utils import parse_html_tags

solution_template: str = r'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem {problem_number}
# https://projecteuler.net/problem={problem_number}
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={default_kwargs}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem {problem_number}
    https://projecteuler.net/problem={problem_number}
    {problem_content}
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
'''


def get_module_content(problem_number: int, problem_content: str) -> str:
    return solution_template.format(problem_number=problem_number, problem_content=parse_html_tags(problem_content),
                                    default_kwargs='{}')
