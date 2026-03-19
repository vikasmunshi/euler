#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
"""
from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from bs4 import BeautifulSoup

from solver.download import download_file
from solver.workspace import PROJECTEULER_URL, PROBLEMS_LIST_URL, WORKSPACE_DIR, clear_workspace

__all__ = [
    'PROBLEMS',
    'ProjectEulerFiles',
    'init_from_projecteuler',
    'seed_problem_statement_cache',
]


class ProjectEulerFiles(StrEnum):
    problem_number_file = 'number.txt'
    problem_resources_dir = 'resources'
    problem_statement_html_file = 'problem.html'
    problem_statement_md_file = 'problem.md'
    problem_title_file = 'title.txt'
    problem_url_file = 'url.txt'


PROBLEMS: list[int] = [int(line.split('##')[0]) for line in download_file(PROBLEMS_LIST_URL).strip().splitlines()[1:]]


def seed_problem_statement_cache(problems: list[int] | None = None, force_refresh: bool = False) -> None:
    global PROBLEMS
    if force_refresh:
        PROBLEMS = [int(line.split('##')[0])
                    for line in download_file(PROBLEMS_LIST_URL, force_refresh=force_refresh).strip().splitlines()[1:]]
    for problem_number in problems or PROBLEMS:
        clear_workspace()
        init_from_projecteuler(problem_number, force_refresh=force_refresh)


def init_from_projecteuler(problem_number: int, force_refresh: bool = False) -> None:
    if WORKSPACE_DIR.exists():
        print('Workspace already exists, clear it before re-initializing')
        return
    problem_url: str = f'{PROJECTEULER_URL}/problem={problem_number}'
    try:
        problem_html: str = download_file(problem_url, force_refresh=force_refresh)
    except Exception as e:
        raise RuntimeError(f'Failed to download problem {problem_number} from {problem_url}: {e}') from e
    html_content, title_content, md_content, resources = parse_html(problem_html, problem_number, force_refresh)
    print('Initializing workspace.')
    print(f'{problem_number=} {title_content=} {problem_url=}')

    def write_file(filename: str, file_content: str) -> None:
        filepath: Path = WORKSPACE_DIR / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(file_content)
        print(f'\t{filepath}')

    write_file(ProjectEulerFiles.problem_number_file, str(problem_number))
    write_file(ProjectEulerFiles.problem_statement_html_file, html_content)
    write_file(ProjectEulerFiles.problem_statement_md_file, md_content)
    write_file(ProjectEulerFiles.problem_title_file, title_content)
    write_file(ProjectEulerFiles.problem_url_file, problem_url)
    for resource_filename, content in resources.items():
        write_file(f'{ProjectEulerFiles.problem_resources_dir}/{resource_filename}', content)
    print('Workspace initialized.')


def parse_html(problem_html: str, problem_number: int, force_refresh: bool) -> tuple[str, str, str, dict[str, str]]:
    problem_soup: BeautifulSoup = BeautifulSoup(problem_html, 'html.parser')
    problem_content_obj: BeautifulSoup | None = problem_soup.find('div', {'class': 'problem_content'})
    if not problem_content_obj:
        raise ValueError(f'Problem {problem_number}: Could not find problem_content div in HTML')
    problem_content: str = problem_content_obj.text.strip()
    title_obj: BeautifulSoup | None = problem_soup.find('h2')
    md_content: str = f'# {title_obj.text.strip()}\n\n{problem_content}'
    if not title_obj:
        raise ValueError(f'Problem {problem_number}: Could not find h2 title element in HTML')
    html_content = problem_html
    title_content: str = title_obj.text.strip()
    resources: dict[str, str] = {}
    for resource in (u for a in problem_content_obj.find_all('a') if (u := a.get('href', '')).startswith('resources/')):
        resource_filename: str = resource.split('/')[-1]
        try:
            content: str = download_file(f'{PROJECTEULER_URL}/{resource.lstrip('/')}', force_refresh=force_refresh)
        except Exception as e:
            print(f'Warning: Failed to download resource {resource}: {e}')
        else:
            resources[resource_filename] = content
    return html_content, title_content, md_content, resources
