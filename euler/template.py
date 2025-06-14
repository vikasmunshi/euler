#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from euler.utils import parse_html_tags

solution_template: str = r"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem {problem_number}
# https://projecteuler.net/problem={problem_number}
# Answer: 
# Notes: 
import textwrap
from typing import Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={{}},
        answer=None,
    ),
]


def solution(*, kwarg: Any) -> Any:
    # enter the solution here
    return None


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent('''
solution to Project Euler problem {problem_number}
https://projecteuler.net/problem={problem_number}
{problem_content}
''').strip()

if __name__ == '__main__':
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    args = parser.parse_args()
    logger.setLevel(args.log_level)
    timeout, max_workers = args.timeout, args.max_workers

    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
""".strip('\n')


def get_module_content(problem_number: int, problem_content: str) -> str:
    return solution_template.format(problem_number=problem_number, problem_content=parse_html_tags(problem_content))
