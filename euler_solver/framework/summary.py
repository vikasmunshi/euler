#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Summary for Project Euler problems."""
from __future__ import annotations

from importlib import import_module
from json import load
from math import isfinite
from pathlib import Path
from re import DOTALL, MULTILINE, sub
from textwrap import fill
from types import ModuleType
from typing import Any, cast

import pandas as pd

from euler_solver.framework.logger import logger
from euler_solver.framework.paths import base_dir, get_evaluation_log_path, get_module_fqdn, get_module_path
from euler_solver.framework.register import format_kwargs


def create_summary(history_file: str, problems_file: str) -> None:
    from euler_solver.args import parser  # defer import to avoid circular imports
    readme_path: Path = Path('README.md')
    readme_content: str = readme_path.read_text(encoding='utf-8')
    readme_content = sub(r"```[^\n]*\nusage: [^`]*```", f"```text\n{parser.format_help()}```", readme_content,
                         flags=MULTILINE | DOTALL)
    readme_content = sub(r'^## Summary Dashboard.*', '## Summary Dashboard\n\n', readme_content,
                         flags=MULTILINE | DOTALL)
    readme_content = '\n'.join(line.rstrip() for line in readme_content.splitlines(keepends=False)) + '\n'
    summary_content: str = create_summary_markdown_with_widths(history_file, problems_file)
    readme_path.write_text(readme_content + summary_content, encoding='utf-8')


def create_summary_markdown_with_widths(history_file: str, problems_file: str) -> str:
    logger.setLevel('ERROR')
    history_df: pd.DataFrame = load_history(history_file, problems_file)

    # Markdown table header with alignment
    markdown_content = (
        '### Summary of Project Euler Solutions\n\n'
        '| Status | Number | Name                          | Solved On   | Execution Time        | Solution  |\n'
        '|:------:|-------:|:------------------------------|:------------|----------------------:|:---------:|\n'
    )
    for _, row in history_df.iterrows():
        # Extract problem details
        execution_time: float = row.get('execution_time', float('nan'))
        name: str = cast(str, row.get('problem_name', '...'))
        name = fill(name, width=42).replace('\n', '<BR>') if len(name) > 42 else name
        number: int = cast(int, row.get('problem_number'))
        py_file_name: str = get_module_path(number).relative_to(base_dir).as_posix()
        solved_on: str = row['solved_datetime'].strftime('%Y-%m-%d') if pd.notna(row['solved_datetime']) else ''
        if row.get('solved'):
            if execution_time <= 1.0:
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
        et_str: str = f'{int(execution_time * 1e6):_} µs' if pd.notna(execution_time) else ''
        markdown_content += f'| {status} | {number:>6} | {name} | {solved_on:<12} | {et_str:>16} | {link} |\n'
    return markdown_content


def load_history(history_file: str, problems_file: str) -> pd.DataFrame:
    print(f'download {history_file} and {problems_file} from https://projecteuler.net/')
    input('Press Enter to continue...')

    # Load history_file (no headers)
    history_column_names: list[str] = ['irrelevant_id', 'solved_datetime', 'problem_number', 'problem_name']
    history_df: pd.DataFrame = pd.read_csv(history_file, header=None, names=history_column_names)
    history_df = history_df[['problem_number', 'solved_datetime']]
    history_df['problem_number'] = history_df['problem_number'].astype(int)
    history_df['solved_datetime'] = pd.to_datetime(history_df['solved_datetime'], format='%d %b %y (%H:%M)', utc=True)

    # Load problems_file (has headers)
    fix_pe_problem_file(problems_file)
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


def fix_pe_problem_file(problems_file: str) -> None:
    problems_path: Path = Path(problems_file)
    content: list[str] = problems_path.read_text(encoding='utf-8').splitlines()
    content[0] = '"ID","Title","Published","Solved By","Last Poster","Last Post Date","Solve Status"'
    problems_path.write_text('\n'.join(content), encoding='utf-8')


def get_execution_time(euler_problem: int) -> float | None:
    answers_file: Path = get_evaluation_log_path(euler_problem)
    if not answers_file.exists():
        return None
    test_case_evaluation_log: dict[str, Any] = load(answers_file.open('r'))
    if not test_case_evaluation_log:
        return None
    module: ModuleType = import_module(get_module_fqdn(euler_problem))
    test_case: dict[str, Any] = next((tc for tc in getattr(module, 'test_cases') if tc['category'] == 'main'), {})
    if not test_case:
        return None
    test_case_key: str = format_kwargs(test_case['input'])
    test_case_key = f'({test_case_key})'
    et_list: list[float] = [v for k, v in test_case_evaluation_log.items() if k.endswith(test_case_key) and isfinite(v)]
    if not et_list:
        return None
    execution_time: float = min(et_list)
    return execution_time
