#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from shutil import rmtree

from bs4 import BeautifulSoup

from solver.download import download_file
from solver.workspace import PROJECTEULER_URL, PROBLEMS_LIST_URL, WORKSPACE_DIR

__all__ = [
    'DEFAULT_FILES_SET',
    'ProjectEulerFiles',
    'cache_stack',
    'init_from_projecteuler',
]


class ProjectEulerFiles(StrEnum):
    problem_number_file = 'number.txt'
    problem_resources_dir = 'resources'
    problem_statement_html_file = 'problem.html'
    problem_statement_md_file = 'problem.md'
    problem_title_file = 'title.txt'
    problem_url_file = 'url.txt'

    @property
    def path(self) -> Path:
        return WORKSPACE_DIR / self.value


DEFAULT_FILES_SET: set[str] = {v.value for v in ProjectEulerFiles}


def cache_stack(problems: list[int] | None = None, refresh_list: bool = False, refresh_problems: bool = False) -> None:
    if problems is None:
        problems = [int(line.split('##')[0])
                    for line in download_file(PROBLEMS_LIST_URL, force_refresh=refresh_list).strip().splitlines()[1:]]
    for problem_number in problems:
        init_from_projecteuler(problem_number, force_refresh=refresh_problems)
        print(f'Stack cached for {problem_number}')


def init_from_projecteuler(problem_number: int, force_refresh: bool = False) -> None:
    problem_url: str = f'{PROJECTEULER_URL}/problem={problem_number}'
    try:
        problem_html: str = download_file(problem_url, force_refresh=force_refresh)
    except Exception as e:
        raise RuntimeError(f'Failed to download problem {problem_number} from {problem_url}: {e}') from e
    problem_soup: BeautifulSoup = BeautifulSoup(problem_html, 'html.parser')
    problem_content_obj: BeautifulSoup | None = problem_soup.find('div', {'class': 'problem_content'})
    if not problem_content_obj:
        raise ValueError(f'Problem {problem_number}: Could not find problem_content div in HTML')
    problem_content: str = problem_content_obj.text.strip()
    title_obj: BeautifulSoup | None = problem_soup.find('h2')
    if not title_obj:
        raise ValueError(f'Problem {problem_number}: Could not find h2 title element in HTML')
    problem_title: str = title_obj.text.strip()
    if WORKSPACE_DIR.exists():
        rmtree(WORKSPACE_DIR, ignore_errors=True)
    ProjectEulerFiles.problem_resources_dir.path.mkdir(parents=True, exist_ok=True)
    ProjectEulerFiles.problem_number_file.path.write_text(str(problem_number))
    ProjectEulerFiles.problem_statement_html_file.path.write_text(problem_html)
    ProjectEulerFiles.problem_statement_md_file.path.write_text(problem_title + '\n\n' + problem_content)
    ProjectEulerFiles.problem_title_file.path.write_text(problem_title)
    ProjectEulerFiles.problem_url_file.path.write_text(problem_url)
    print(f'Initialized workspace for {problem_number} from {problem_url}')
    for resource in (u for a in problem_content_obj.find_all('a')
                     if (u := a.get('href', '')).startswith('resources/')):
        resource_filename: str = resource.split('/')[-1]
        try:
            content: str = download_file(f'{PROJECTEULER_URL}/{resource.lstrip('/')}', force_refresh=force_refresh)
        except Exception as e:
            print(f'Warning: Failed to download resource {resource}: {e}')
        else:
            resource_filepath: Path = ProjectEulerFiles.problem_resources_dir.path / resource_filename
            resource_filepath.write_text(content)
            print(f'Downloaded resource {resource_filename} to {resource_filepath}')
    for _ in ProjectEulerFiles.problem_resources_dir.path.iterdir():
        break
    else:
        ProjectEulerFiles.problem_resources_dir.path.rmdir()
