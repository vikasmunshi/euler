#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utility function for gathering problem inputs for AI """
from __future__ import annotations

from json import JSONDecodeError, loads
from typing import Any, NamedTuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from solver.core.config import Config
from solver.core.problems import Problem
from solver.core.results import Result, read_results
from solver.core.solution_notes import get_solution_notes_html
from solver.core.stack import read_stack_file, stack_base_dir
from solver.utils.download import download_file
from solver.utils.path_utils import iterdir_recursive
from solver.core.problems import solutions_history


class Facts(NamedTuple):
    difficulty: str
    number: int
    problem_content: str
    results: str
    solution_notes: str
    solutions: str
    solved_date: str
    test_cases: str
    title: str


def format_results_markdown(solved_results: list[Result]) -> str:
    if not solved_results:
        return '(no benchmark results available)'
    rows = ['| solution | category | args | answer | verdict | elapsed (s) |',
            '|---|---|---|---|---|---|']
    for r in solved_results:
        rows.append(f'| {r.solution} | {r.category} | {r.args} | {r.answer} '
                    f'| {r.verdict} | {r.average:.4f} |')
    return '\n'.join(rows)


def format_solutions_markdown(solutions: dict[str, str]) -> str:
    parts: list[str] = []
    for filename, source in solutions.items():
        lang = 'c' if filename.endswith('.c') else 'python'
        parts.append(f'### {filename}\n```{lang}\n{source}\n```')
    return '\n\n'.join(parts)


def format_test_cases_markdown(test_cases: list[dict[str, Any]]) -> str:
    if not test_cases:
        return '(no test cases available)'
    rows = ['| category | input | answer |', '|---|---|---|']
    for tc in test_cases:
        rows.append(f'| {tc.get("category", "")} | {tc.get("input", "")} | {tc.get("answer", "")} |')
    return '\n'.join(rows)


def gather_facts(problem_number: int, strict: bool = False) -> Facts:
    """
    Gathers and processes facts from the 'stack' about a specific problem, including solutions,
    results, test cases, and problem content. This function is used to assemble
    relevant details into a `Facts` object, which contains comprehensive information
    about the problem for further use.

    Arguments:
        problem_number (int): The number of the problem to gather facts about.
        strict (bool): If set to True, enforces strict validation of gathered data
            (e.g., ensures solutions, results, and problem content exist).

    Returns:
        Facts: An object containing all gathered details about the problem,
        including its difficulty, number, title, content, available solutions,
        results, test cases, solution notes, and solved date.

    Raises:
        ValueError: If `strict` is True and any of the required data, such as
        solutions, results, or test cases, is missing or invalid.
    """
    if (problem := Problem.from_number(problem_number)) is None:
        raise ValueError('Invalid problem number')
    solutions: dict[str, str] = {}
    for solution in iterdir_recursive(stack_base_dir(problem.number), rt='str'):
        solution = solution.removesuffix('.enc')
        if not (solution.endswith('.py') or solution.endswith('.c')):
            continue
        solutions[solution] = read_stack_file(problem.number, solution)[0].decode()
    if strict and not solutions:
        raise ValueError('No solutions found')
    solved_results: list[Result] = read_results(problem.number)
    if strict and not solved_results:
        raise ValueError('No results found')
    if strict and not [r for r in solved_results if r.verdict == 'correct' and r.category == 'main']:
        raise ValueError('No solved solutions found')
    test_cases: list[dict[str, Any]]
    try:
        test_cases = loads(read_stack_file(problem.number, Config.test_cases_filename)[0])
    except (FileNotFoundError, JSONDecodeError):
        if strict:
            raise ValueError('No test cases found')
        test_cases = []
    if strict:
        if not [tc for tc in test_cases if tc['answer'] is not None]:
            raise ValueError('No test cases with answers found')
    euler_url: str = urljoin(Config.projecteuler_url, f'problem={problem.number}')
    problem_content: str = ''
    if problem_html := download_file(euler_url, refresh=False):
        problem_soup: BeautifulSoup = BeautifulSoup(problem_html, 'html.parser')
        problem_content = str(problem_soup.find('div', {'class': 'problem_content'}) or '')
        if not problem_content:
            if strict:
                raise ValueError('No problem content found')
    solution_notes: str = get_solution_notes_html(problem.number)
    if Config.default_solution_notes in solution_notes:
        solution_notes = ''
    solved_date: str = solutions_history.get(problem.number, 'unknown')
    return Facts(
        difficulty=problem.difficulty,
        number=problem.number,
        problem_content=problem_content,
        results=format_results_markdown(solved_results),
        solution_notes=solution_notes,
        solutions=format_solutions_markdown(solutions),
        solved_date=solved_date,
        test_cases=format_test_cases_markdown(test_cases),
        title=problem.title,
    )


__all__ = ('Facts', 'gather_facts', 'format_solutions_markdown')
