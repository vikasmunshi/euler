#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Project Euler scraper: fetches problem pages and builds standalone HTML with test cases and solution approach."""
from __future__ import annotations

from itertools import chain
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from bs4.element import AttributeValueList, Tag

from solver.config import config
from solver.core.problems import Problem, problems
from solver.shell import console
from solver.templates.engine import Templates, get_template
from solver.utils.download import download_file


def clean_html_for_local(*,
                         content: str,
                         euler_url: str,
                         github_url: str,
                         summary_url: str,
                         next_url: str,
                         previous_url: str,
                         problem: Problem,
                         ) -> bytes:
    """
    Wrap problem content in a self-contained HTML page suitable for local viewing.

    The test cases, results, and notes sections are rendered client-side by problem.js,
    which fetches test_cases.json, results.json, and notes.html at view time.

    Args:
        content:                The Parsed HTML of the problem content div.
        euler_url:              The URL of the problem on projecteuler.net.
        github_url:             The URL of the problem on GitHub.
        summary_url:            The URL of the summary page.
        next_url:               The URL of the next problem.
        previous_url:           The URL of the previous problem.
        problem:                The Project Euler problem metadata.

    Returns:
        A complete HTML document as UTF-8 encoded bytes.
    """
    content = '>\n<'.join(content.split('><'))
    tab: str = ' ' * 8
    content = '\n'.join(tab + line.strip() for line in content.splitlines() if line.strip()).lstrip(' ')
    html: str = get_template(Templates.PROBLEM).substitute(
        content=content,
        euler_url=euler_url,
        github_url=github_url,
        summary_url=summary_url,
        next_url=next_url,
        previous_url=previous_url,
        problem_number=problem.number,
        title=problem.as_title(),
    )
    return html.encode('utf-8')


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


def problem_nav_urls(problem_number: int, /) -> tuple[str, str, str, str, str]:
    """Return the canonical and relative navigation URLs for a problem's HTML page.

    Args:
        problem_number: The Project Euler problem number.

    Returns:
        A 5-tuple of "(euler_url, github_url, next_url, previous_url, summary_url)"
        where "euler_url" is the canonical path to the current problem's directory
        (used as the base for GitHub links and asset paths), and
        "next_url" / "previous_url" are paths relative to that directory pointing
        to the adjacent problems' "problem.html" files (suitable for use as "href"
        values in the page).
        Navigation wraps around: problem 1's previous is the last problem, and
        the last problem's next is problem 1.
        "summary_url" is the path to the index page.
    """
    max_problem_number: int = problems.problems_list[-1].number
    euler_url: str = urljoin(config.projecteuler_url, f'problem={problem_number}')
    github_url: str = (f'{config.project_git_url}/blob/master/'
                       f'{config.solutions_dir.name}/{'/'.join([*f'{problem_number:04d}'])}/')
    next_problem: int = (problem_number % max_problem_number) + 1
    previous_problem: int = ((problem_number - 2) % max_problem_number) + 1
    next_url: str = '/' + '/'.join(f'{next_problem:04d}') + '/problem.html'
    previous_url: str = '/' + '/'.join(f'{previous_problem:04d}') + '/problem.html'
    summary_url: str = '/index.html'
    return euler_url, github_url, next_url, previous_url, summary_url


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
    euler_url, github_url, next_url, previous_url, summary_url = problem_nav_urls(problem_number)
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
    html: bytes = clean_html_for_local(content=str(content),
                                       euler_url=euler_url,
                                       github_url=github_url,
                                       summary_url=summary_url,
                                       next_url=next_url,
                                       previous_url=previous_url,
                                       problem=problem, )
    files[config.statement_filename] = html
    return problem, files


__all__ = ('problem_statement', 'extract_resources')
