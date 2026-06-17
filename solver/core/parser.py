#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""HTML problem-statement parser: assemble a standalone statement page from a scraped Project Euler page."""
from __future__ import annotations

__all__ = ['problem_statement', 'extract_resources']

from itertools import chain
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from bs4.element import AttributeValueList, Tag

from solver.config import config
from solver.core.problems import Problem
from solver.shell import console
from solver.utils.download import download_file


def extract_resources(problem_content: Tag, *, force_refresh: bool) -> dict[str, bytes]:
    """
    Download all linked resources (images, files) referenced in problem content.

    Updates the href and src attributes of <a> and <img> tags in-place to point
    to their local resource paths.

    Args:
        problem_content: Parsed HTML root to scan; typically the problem content div but
                         any Tag (including a full BeautifulSoup document) works.
        force_refresh:   If True, re-download resources even if cached.

    Returns:
        A mapping of local resource file paths to their downloaded content.
    """
    solved_results: dict[str, bytes] = {}
    for element in chain(problem_content.find_all('a'), problem_content.find_all('img')):
        attr: str = {'a': 'href', 'img': 'src'}[element.name]
        src: str | AttributeValueList | None = element.get(attr)
        if src is None:
            continue
        if isinstance(src, str) and (src.startswith('resources/') or src.startswith('project/images/')):
            url: str = urljoin(config.projecteuler_url, src)
            local_filename: str = config.resource_dirname + '/' + src.split('/')[-1].split('?')[0]
            if (content := download_file(url, refresh=force_refresh)) is None:
                console.print(f'[error]error:[/error] failed to download [accent]{local_filename}[/accent] from {url}')
                continue
            solved_results[local_filename] = content
            element[attr] = local_filename
    return solved_results


def problem_statement(problem_number: int, /, *, force_refresh: bool = False, ) -> tuple[Problem, dict[str, bytes]]:
    """
    Fetch and assemble the full problem statement for a Project Euler problem.

    Downloads the problem HTML and extracts linked resources (images, files). Builds a
    standalone HTML file containing the problem content, a refreshed test cases section,
    and a preserved solution approach section.

    Args:
        problem_number:     The Project Euler problem number to fetch.
        force_refresh:      If True, re-download the problem HTML and resources even if cached.

    Returns:
        A mapping of relative file paths to file contents, including the local HTML file
        and any downloaded resource files.

    Raises:
        ValueError: If the problem HTML cannot be downloaded or the problem content div is missing.
    """
    if (problem := Problem.from_number(problem_number)) is None:
        raise ValueError(f'Problem {problem_number}: Invalid problem number')
    euler_url = urljoin(config.projecteuler_url, f'problem={problem_number}')
    if (problem_html := download_file(euler_url, refresh=force_refresh)) is None:
        raise ValueError(f'Problem {problem.number}: Failed to download HTML from {euler_url}')
    problem_soup: BeautifulSoup = BeautifulSoup(problem_html, 'html.parser')
    content: BeautifulSoup = problem_soup.find('div', {'class': 'problem_content'})  # type: ignore [assignment]
    if not content:
        raise ValueError(f'Problem {problem.number}: Could not find problem_content div in HTML')
    files: dict[str, bytes] = extract_resources(
        content,  # extract_resources rewrites href and src attributes in content
        force_refresh=force_refresh
    )
    files[config.statement_filename] = str(content).encode('utf-8')
    return problem, files
