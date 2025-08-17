#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Summary for Project Euler problems."""
from __future__ import annotations

from importlib import import_module
from json import load
from pathlib import Path
from re import DOTALL, MULTILINE, Pattern, compile
from textwrap import fill
from types import ModuleType
from typing import Any, cast

import pandas as pd

from euler_solver.logger import logger
from euler_solver.setup.paths import base_dir, get_answers_path, get_module_fqdn, get_module_path
from euler_solver.setup.register import SolutionRegistry
from euler_solver.utils.human_readable_time import human_readable_seconds, seconds_from_human_readable

summary_re: Pattern[str] = compile(r'^## Summary Dashboard.*', MULTILINE | DOTALL)


def create_summary() -> None:
    create_summary_markdown_with_widths()
    readme_path: Path = Path('README.md')
    summary_path: Path = Path('summary/summary.md')
    readme_content: str = readme_path.read_text(encoding='utf-8')
    summary_content: str = summary_path.read_text(encoding='utf-8')
    updated_content: str = summary_re.sub('## Summary Dashboard\n\n', readme_content) + summary_content
    readme_path.write_text(updated_content, encoding='utf-8')


def create_summary_markdown_with_widths() -> None:
    logger.setLevel('ERROR')
    summary_file: Path = Path('summary/summary.md')
    history_df: pd.DataFrame = load_history()

    # Markdown table header with alignment
    markdown_content = (
        '### Summary of Project Euler Solutions\n\n'
        '| Status | Number | Name                          | Solved On   | Execution Time        | Solution  |\n'
        '|:------:|-------:|:------------------------------|:------------|----------------------:|:---------:|\n'
    )
    for _, row in history_df.iterrows():
        # Extract problem details
        execution_time: str = row.get('execution_time', '')
        name: str = cast(str, row.get('problem_name', '...'))
        name = fill(name, width=42).replace('\n', '<BR>') if len(name) > 42 else name
        number: int = cast(int, row.get('problem_number'))
        py_file_name: str = get_module_path(number).relative_to(base_dir).as_posix()
        solved_on: str = row['solved_datetime'].strftime('%Y-%m-%d') if pd.notna(row['solved_datetime']) else ''
        if row.get('solved'):
            if execution_time.endswith('-sec'):
                status = '\U0001F7E9'  # 🟩 green (escaped Unicode)
            else:
                status = '\U0001F7E7'  # 🟧 orange (escaped Unicode)
        else:
            status = '\U0001F7E5'  # 🟥 red (escaped Unicode)
        name = f'[{name}](https://projecteuler.net/problem={number})'
        if py_file_name.endswith('private.py'):
            py_file_name += 'i'
        link = f'[solution](euler_solver/{py_file_name})'
        # Add a row to the Markdown table
        markdown_content += f'| {status} | {number:>6} | {name} | {solved_on:<12} | {execution_time:>20} | {link} |\n'
    # Write the Markdown file with table content
    summary_file.write_text(markdown_content, encoding='utf-8')


def load_history() -> pd.DataFrame:
    history_file: Path = Path('summary/history.csv')
    problems_file: Path = Path('summary/pe_minimal_problems.csv')
    print(f'download {history_file.as_posix()} and {problems_file.as_posix()} from https://projecteuler.net/')
    input('Press Enter to continue...')

    # Load history_file (no headers)
    history_column_names: list[str] = ['irrelevant_id', 'solved_datetime', 'problem_number', 'problem_name']
    history_df: pd.DataFrame = pd.read_csv(history_file, header=None, names=history_column_names)
    history_df = history_df[['problem_number', 'solved_datetime']]
    history_df['problem_number'] = history_df['problem_number'].astype(int)
    history_df['solved_datetime'] = pd.to_datetime(history_df['solved_datetime'], format='%d %b %y (%H:%M)', utc=True)

    # Load problems_file (has headers)
    problems_df: pd.DataFrame = pd.read_csv(problems_file)
    # Ensure ID in problems_df is of type int64 for merging
    problems_df['ID'] = problems_df['ID'].astype(int)

    # Merge the two dataframes on the problem number (history_df.problem_number <-> problems_df.ID)
    merged_df: pd.DataFrame = pd.merge(problems_df, history_df, left_on='ID', right_on='problem_number', how='outer')
    merged_df = merged_df[['ID', 'Title', 'Solve Status', 'solved_datetime']]
    merged_df.rename(columns={'ID': 'problem_number'}, inplace=True)
    merged_df.rename(columns={'Title': 'problem_name'}, inplace=True)
    merged_df.rename(columns={'Solve Status': 'solved'}, inplace=True)
    merged_df['solved'] = merged_df['solved'].astype(bool)
    merged_df = merged_df[merged_df['solved']]
    # Enrich execution time
    merged_df['execution_time'] = merged_df['problem_number'].apply(get_execution_time)
    return merged_df


def get_execution_time(euler_problem: int) -> str:
    answers_file: Path = get_answers_path(euler_problem)
    if not answers_file.exists():
        return ''
    test_case_answers: dict[str, Any] = load(answers_file.open('r'))
    if not test_case_answers:
        return ''
    module_name: str = get_module_fqdn(euler_problem)
    module: ModuleType = import_module(module_name)
    test_case: dict[str, Any] = next((tc for tc in getattr(module, 'test_cases') if tc['category'] == 'main'), {})
    if not test_case:
        return ''
    test_case_key: str = SolutionRegistry.format_kwargs(test_case['input'])
    test_case_key = f'_{test_case_key}'
    et_list: list[float] = [seconds_from_human_readable(v)
                            for k, v in test_case_answers.items() if k.endswith(test_case_key)]
    if not et_list:
        return ''
    execution_time: float = min(et_list)
    return human_readable_seconds(execution_time)
