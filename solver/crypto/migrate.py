#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migration script for introducing gitfilter for seamless encryption."""
from __future__ import annotations

from os import utime
from pathlib import Path

from solver.config import config
from solver.core.parser import problem_statement
from solver.core.problems import problems
from solver.core.stack import read_stack_file, stack_base_dir
from solver.utils.path_utils import iterdir_recursive


def migrate() -> int:
    for problem in problems.problems_list:
        current_dir: Path = stack_base_dir(problem.number)
        target_dir: Path = problem.solution_dir
        if not current_dir.exists():
            print(f'Initializing {target_dir.relative_to(config.root_dir)} (no stack directory)...',
                  end=' ')
            _, problem_statement_files = problem_statement(problem.number)
            for filename, content in problem_statement_files.items():
                target_file_path: Path = target_dir.joinpath(filename)
                target_file_path.parent.mkdir(parents=True, exist_ok=True)
                target_file_path.write_bytes(content)
            print('done.')
            continue
        print(f'Migrating {current_dir.relative_to(config.root_dir)} to {target_dir.relative_to(config.root_dir)}...',
              end=' ')
        for filename in iterdir_recursive(current_dir, rt='str'):
            filename = filename.removesuffix('.enc')
            if filename == config.number_filename:
                continue
            content, is_executable, m_time = read_stack_file(problem.number, filename)
            target_file_path = target_dir.joinpath(filename)
            target_file_path.parent.mkdir(parents=True, exist_ok=True)
            target_file_path.write_bytes(content)
            if is_executable:
                target_file_path.chmod(0o755)
            utime(target_file_path, (m_time, m_time))
        print('done.')
    return 0


if __name__ == '__main__':
    raise SystemExit(migrate())
