#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Project Euler scraper: fetches problem pages and builds standalone HTML with test cases and solution approach."""
from __future__ import annotations

from itertools import chain
from json import JSONDecodeError, loads
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from bs4.element import AttributeValueList

from solver.config import problem_statement_filename, projecteuler_url, resource_dirname, test_cases_filename
from solver.download import download_file
from solver.problems import Problem
from solver.stack import read_stack_file

__all__ = ['problem_statement']


def problem_statement(problem_number: int, /, *, force_refresh: bool) -> tuple[Problem, dict[str, bytes]]:
    """
    Fetch and assemble the full problem statement for a Project Euler problem.

    Downloads the problem HTML and extracts linked resources (images, files). Builds a
    standalone HTML file containing the problem content, a refreshed test cases section,
    and a preserved solution approach section.

    Args:
        problem_number: The Project Euler problem number to fetch.
        force_refresh:  If True, re-download the problem HTML and resources even if cached.

    Returns:
        A mapping of relative file paths to file contents, including the local HTML file
        and any downloaded resource files.

    Raises:
        ValueError: If the problem HTML cannot be downloaded or the problem content div is missing.
    """
    if (problem := Problem.from_number(problem_number)) is None:
        raise ValueError(f'Problem {problem_number}: Invalid problem number')
    problem_url: str = urljoin(projecteuler_url, f'problem={problem.number}')
    if (problem_html := download_file(problem_url, refresh=force_refresh)) is None:
        raise ValueError(f'Problem {problem.number}: Failed to download HTML from {problem_url}')
    problem_soup: BeautifulSoup = BeautifulSoup(problem_html, 'html.parser')
    difficulty_level: str = '??'
    if (tooltip := problem_soup.find('span', class_='tooltiptext_right')) and (text := tooltip.get_text()):
        for line in text.split(';'):
            if 'Difficulty level:' in line:
                difficulty_level = line.split(':')[-1].strip()
                break
        else:
            difficulty_level = '--'
    problem = Problem(number=problem.number, title=problem.title, difficulty=difficulty_level)
    problem_content: BeautifulSoup = problem_soup.find('div', {'class': 'problem_content'})  # type: ignore [assignment]
    if not problem_content:
        raise ValueError(f'Problem {problem.number}: Could not find problem_content div in HTML')
    results: dict[str, bytes] = extract_resources(problem_content, force_refresh=force_refresh)
    try:
        test_cases_str: str = read_stack_file(problem.number, test_cases_filename)[0].decode()
        test_cases: str = test_cases_html(problem.number, loads(test_cases_str))
    except (FileNotFoundError, JSONDecodeError):
        test_cases = ''
    solution_notes: str = extract_solution_notes(problem.number)
    html: str = clean_html_for_local(problem_content,
                                     problem=problem,
                                     test_cases=test_cases,
                                     solution_notes=solution_notes)
    results[problem_statement_filename] = html.encode()
    return problem, results


def extract_resources(problem_content: BeautifulSoup, *, force_refresh: bool) -> dict[str, bytes]:
    """
    Download all linked resources (images, files) referenced in problem content.

    Updates the href and src attributes of <a> and <img> tags in-place to point
    to their local resource paths.

    Args:
        problem_content: Parsed HTML of the problem content div.
        force_refresh:   If True, re-download resources even if cached.

    Returns:
        A mapping of local resource file paths to their downloaded content.
    """
    results: dict[str, bytes] = {}
    for element in chain(problem_content.find_all('a'), problem_content.find_all('img')):
        attr: str = {'a': 'href', 'img': 'src'}[element.name]
        src: str | AttributeValueList | None = element.get(attr)
        if src is None:
            continue
        if isinstance(src, str) and (src.startswith('resources/') or src.startswith('project/images/')):
            url: str = urljoin(projecteuler_url, src)
            local_filename: str = resource_dirname + '/' + src.split("/")[-1].split("?")[0]
            if (content := download_file(url, refresh=force_refresh)) is None:
                print(f'Error: Failed to download {local_filename} from {url}')
                continue
            results[local_filename] = content
            element[attr] = local_filename
    return results


def clean_html_for_local(problem_content_obj: BeautifulSoup, *,
                         problem: Problem,
                         test_cases: str = '',
                         solution_notes: str = '',
                         ) -> str:
    """
    Wrap problem content in a self-contained HTML page suitable for local viewing.

    Embeds basic CSS styles and MathJax scripts for rendering mathematical notation,
    and appends a test cases section (always refreshed) and a solution approach section
    (content preserved from the previous version of the file).

    Args:
        problem_content_obj: Parsed HTML of the problem content div.
        problem:             The Project Euler problem number.
        difficulty_level:    The problem difficulty level string (e.g. '20' or '??').
        test_cases:          Inner HTML for the test cases section. Defaults to empty.
        solution_notes:   Inner HTML for the solution approach div. Defaults to empty.

    Returns:
        A complete HTML document string.
    """
    content = BeautifulSoup(str(problem_content_obj), 'html.parser')
    test_cases = test_cases or '<p><em>No test cases available.</em></p>'
    solution_notes = solution_notes or '\n\n'
    return (
        '<!DOCTYPE html>\n'
        '<html>\n'
        '<head>\n'
        '    <meta charset="UTF-8">\n'
        f'    <title>Problem {problem!s}</title>\n'
        '    <style>\n'
        '        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }\n'
        '        .problem_content { line-height: 1.6; }\n'
        '        var { font-style: italic; }\n'
        '        sup { vertical-align: super; font-size: smaller; }\n'
        '        sub { vertical-align: sub; font-size: smaller; }\n'
        '        img { max-width: 100%; height: auto; }\n'
        '        table { border-collapse: collapse; margin: 20px 0; }\n'
        '        td, th { border: 1px solid #ddd; padding: 8px; }\n'
        '        hr { border: none; border-top: 1px solid #ddd; margin: 30px 0; }\n'
        '        h2 { border-bottom: 1px solid #eee; padding-bottom: 6px; }\n'
        '        code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; font-family: monospace; }\n'
        '        #solution-approach-content { min-height: 80px; padding: 12px; background: #f9f9f9; '
        'border: 1px solid #e0e0e0; border-radius: 4px; }\n'
        '    </style>\n'
        '    <script>\n'
        '        MathJax = {\n'
        '            tex: {\n'
        '                inlineMath: [["$", "$"]],\n'
        '                displayMath: [["$$", "$$"]]\n'
        '            }\n'
        '        };\n'
        '    </script>\n'
        '    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>\n'
        '    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">\n'
        '    </script>\n'
        '</head>\n'
        '<body>\n'
        '<section id="problem-statement">\n'
        f'<h2>Problem {problem!s}</h2>\n'
        f'{content}\n'
        '</section>\n'
        '<hr>\n'
        '<section id="test-cases">\n'
        '<h2>Test Cases</h2>\n'
        f'{test_cases}\n'
        '</section>\n'
        '<hr>\n'
        '<section id="solution-notes">\n'
        '<h2>Solution Notes</h2>\n'
        '<div id="solution-notes-content">\n'
        f'{solution_notes}'
        '</div>\n'
        '</section>\n'
        '</body>\n'
        '</html>'
    )


def test_cases_html(problem_number: int, test_cases: list[dict]) -> str:
    """
    Render test cases as HTML sections grouped by category.

    Answers are revealed for problems 1–100 and for 'dev' category test cases;
    all other answers are rendered as '?'.

    Args:
        problem_number: The Project Euler problem number.
        test_cases:     List of test case dicts, each with 'input' and 'category' keys
                        and an optional 'answer' key.

    Returns:
        An HTML string with one <h3>/<ul> block per category.
    """
    sections: dict[str, list[str]] = {}
    for tc in test_cases:
        category: str = tc.get('category', 'extra')
        heading: str = category.capitalize()
        args: str = ', '.join(f'{k}={v!r}' for k, v in tc['input'].items())
        ans: Any = tc.get('answer')
        answer: str = repr(ans) if ans is not None and (problem_number <= 100 or category == 'dev') else '?'
        sections.setdefault(heading, []).append(
            f'<li><code>solve({args})</code> → <code>{answer}</code></li>'
        )
    parts: list[str] = []
    for heading, items in sections.items():
        parts.append(f'<h3>{heading}</h3>\n<ul>\n' + '\n'.join(items) + '\n</ul>')
    return '\n'.join(parts)


def extract_solution_notes(problem_number: int) -> str:
    """
    Extract the inner HTML of the solution notes div from the existing HTML stack file.

    Args:
        problem_number: The Project Euler problem number.

    Returns:
        The inner HTML string of the solution notes div, or an empty string if the
        file does not exist or the div is absent.
    """
    try:
        html_bytes: bytes = read_stack_file(problem_number, problem_statement_filename)[0]
        soup: BeautifulSoup = BeautifulSoup(html_bytes.decode(), 'html.parser')
        if div := soup.find('div', id='solution-notes-content'):
            return div.decode_contents()
        return ''
    except FileNotFoundError:
        return ''
