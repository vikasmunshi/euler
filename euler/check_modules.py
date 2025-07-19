#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import pathlib
import subprocess
from operator import itemgetter
from typing import Dict, Set

from euler.evaluator import solutions
from euler.loader import get_module_path, module_name
from euler.logger import logger
from euler.template import main_block


def check_file_is_committed(file_path: pathlib.Path) -> bool:
    if file_path.exists():
        git_cmd = f'git log -1 -- {file_path.relative_to(pathlib.Path(__file__).parent.parent).as_posix()}'
        log_result = subprocess.run(git_cmd.split(), capture_output=True, text=True, check=False)
        return bool(log_result.stdout.strip())
    return False


def check_modules(first_problem_number: int | None = None, last_problem_number: int | None = None,
                  check_uncommitted: bool = False, ) -> int:
    solutions_dir: pathlib.Path = pathlib.Path(__file__).parent / 'solutions'
    logger.info(f'Checking solution modules in {solutions_dir} {first_problem_number=} {last_problem_number=} ...')
    if first_problem_number is None or last_problem_number is None:
        solutions_modules: Dict[str, int] = {module_name(problem_number := int(m.stem[-6:])): problem_number
                                             for m in solutions_dir.glob('**/*.py') if m.name != '__init__.py'
                                             if check_uncommitted or check_file_is_committed(m)}
        logger.info(f'Found {len(solutions_modules)} solution modules.')
    else:
        solutions_modules = {module_name(problem_number): problem_number
                             for problem_number in range(first_problem_number, last_problem_number + 1)
                             if check_file_is_committed(get_module_path(problem_number))}
    failed_modules: Set[str] = set()
    for module, problem_number in sorted(solutions_modules.items(), key=itemgetter(0)):
        existing_solutions: Set[int] = set(solutions.keys())
        importlib.import_module(module)
        new_solutions: Set[int] = set(solutions.keys()) - existing_solutions
        if len(new_solutions) == 0:
            logger.info(f'Module {module} does not register a solution function.')
            failed_modules.add(module.split('.')[-1])
        elif len(new_solutions) == 1:
            solution_number: int = new_solutions.pop()
            if solution_number == problem_number:
                logger.info(f'Module {module} registers solution for #{problem_number}.')
            else:
                failed_modules.add(module.split('.')[-1])
                logger.info(f'Module {module} registers solution for #{solution_number} instead of #{problem_number}.')
        else:
            failed_modules.add(module.split('.')[-1])
            logger.info(f'Module {module} registers solutions for multiple problems: {new_solutions}.')
    module_files: Dict[pathlib.Path, int] = {get_module_path(problem_number=problem_number): problem_number
                                             for problem_number in solutions_modules.values()}
    for module_file, problem_number in module_files.items():
        with module_file.open('r') as f:
            content = f.read().strip('\n')
        if not content.endswith(main_block):
            failed_modules.add(module_file.stem)
            logger.error(f'Module {module_file.stem} does not end with a main block.')
        for expected in (f'URL: https://projecteuler.net/problem={problem_number}',
                         f'# The problem number from Project Euler (https://projecteuler.net/problem={problem_number})',
                         f'problem_number: int = {problem_number}',):
            if expected not in content:
                failed_modules.add(module_file.stem)
                logger.error(f'Module {module_file.stem} does not contain the expected line: {expected}')
    if not failed_modules:
        logger.info('All solution modules are valid.')
    else:
        logger.error(f'Failed modules: {", ".join(sorted(failed_modules))}')
    return len(failed_modules)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(check_modules(check_uncommitted=True))
