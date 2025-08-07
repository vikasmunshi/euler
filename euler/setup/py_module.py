#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python Module Utility for Project Euler problems."""
from __future__ import annotations

from fcntl import LOCK_EX, LOCK_UN, flock
from pathlib import Path
from re import DOTALL, MULTILINE, compile
from typing import Any, TYPE_CHECKING

from euler.setup.test_case import TestCase, TestCaseCategory

if TYPE_CHECKING:
    from euler.setup.solution_info import SolutionInfo

shebang_lines_re = compile(r'#\s?!.*\n#.*\n', MULTILINE)
triple_quote_re = compile(r'(r?""".*?"""\s*\n|' + r"r?'''.*?'''\s*\n)", DOTALL)
main_block_re = compile(r'if __name__ == \'__main__\':\n.*', DOTALL)
trailing_whitespace_re = compile(r'(\s+)$')
empty_test_case_kwargs_re = compile(r'^\s*,\n', MULTILINE)


def get_module_source_code(info: SolutionInfo, py_file: Path, hide_answers: bool = False) -> str:
    tab = ' ' * 4
    doc_string, kwargs_str, return_type = get_docstring(info, hide_answers)
    if py_file.exists():
        with open(py_file, 'r') as f:
            flock(f.fileno(), LOCK_EX)
            source_code: str = f.read()
            flock(f.fileno(), LOCK_UN)
        source_code = shebang_lines_re.sub('', source_code, count=0)
        source_code = triple_quote_re.sub('', source_code, count=1)
        source_code = main_block_re.sub('', source_code)
        if 'from __future__ import annotations' not in source_code:
            source_code = "from __future__ import annotations\n\n" + source_code.lstrip('\n')
    else:
        if kwargs_str:
            function_def: str = f'def {info.problem_name}(*, {kwargs_str}) -> {return_type}:'
        else:
            function_def = f'def {info.problem_name}() -> {return_type}:'
        source_code = ("from __future__ import annotations\n\n"
                       "from euler.logger import logger\n"
                       "from euler.setup import TestCaseCategory, evaluate, register_solution\n\n\n"
                       f"@register_solution(euler_problem={info.euler_problem}, "
                       "test_case_category=TestCaseCategory.EXTENDED)\n"
                       f"{function_def}\n"
                       f"{tab}raise NotImplementedError()\n\n\n")
    header: str = '#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n'
    main_block: str = (f"if __name__ == '__main__':\n"
                       f"{tab}logger.setLevel('ERROR')\n"
                       f"{tab}raise SystemExit(evaluate(euler_problem={info.euler_problem}, "
                       "time_out_in_seconds=300, mode='evaluate'))\n")
    source_code = header + doc_string + source_code + main_block
    source_code = trailing_whitespace_re.sub('', source_code)
    return source_code + '\n'


def get_docstring(info: SolutionInfo, hide_answers: bool = False) -> tuple[str, str, str]:
    tab: str = ' ' * 2
    if hide_answers:
        test_cases: list[TestCase] = [TestCase.from_dict(test_case.as_dict()) for test_case in info.test_cases]
    else:
        test_cases = info.test_cases
    classified_test_cases: dict[TestCaseCategory, list[TestCase]] = {}
    for test_case in test_cases:
        classified_test_cases.setdefault(test_case.test_case_category, []).append(test_case)
    if classified_test_cases and len(classified_test_cases[TestCaseCategory.MAIN]) == 1:
        main_test_case: TestCase = classified_test_cases[TestCaseCategory.MAIN][0]
        answer: Any = main_test_case.result
        kwargs_str: str = ', '.join(f'{k}: {type(v).__name__}' for k, v in main_test_case.kwargs.items())
        return_type: str = type(answer or test_cases[0].result or 0).__name__
        test_cases_str: str = get_test_cases_str(classified_test_cases, tab)
    else:
        answer = None
        kwargs_str = 'n: int'
        return_type = 'int'
        test_cases_str = ''
    problem_name = info.problem_name.replace('_', ' ').title()
    doc_string: str = ('r"""\n'
                       f'{tab}Project Euler Problem {info.euler_problem}: {problem_name}.\n\n'
                       f'{tab}Problem Statement:\n{info.problem_statement}\n\n'
                       f'{tab}Solution Approach:\n{info.solution_approach}\n\n'
                       f'{tab}Test Cases:\n{test_cases_str}\n\n'
                       f'{tab}Answer: {answer}\n'
                       f'{tab}URL: {info.url}\n'
                       '"""\n')
    return doc_string, kwargs_str, return_type


def get_test_cases_str(classified_test_cases: dict[TestCaseCategory, list[TestCase]], tab: str) -> str:
    test_cases_str: str = '\n'.join(
            f'{tab * 2}{cat}:\n'
            f'{tab * 3}{f"\n{tab * 3}".join(f"{f',\n{tab * 3}'.join(f'{k}={v}' for k, v in tc.kwargs.items())},\n"
                                            f"{tab * 3}answer={tc.result}.\n{tab * 3}" for tc in cases)}'
            for cat, cases in classified_test_cases.items())
    test_cases_str = ''.join(split_long_line(line) for line in test_cases_str.splitlines(keepends=True))
    test_cases_str = empty_test_case_kwargs_re.sub('', test_cases_str)
    return test_cases_str


def split_long_line(line: str, max_width: int = 80, tab_width: int = 0) -> str:
    if len(line) <= max_width:
        return line
    if 'url=https://projecteuler.net/resources/documents/' in line:
        return line
    tab_width = ((line.rfind('=') + 1) or (line.rfind(' ') + 1)) if tab_width == 0 else tab_width
    if tab_width >= max_width:
        return line
    return (line[:max_width] + '\n' +
            split_long_line(' ' * tab_width + line[max_width:], max_width=max_width, tab_width=tab_width))
