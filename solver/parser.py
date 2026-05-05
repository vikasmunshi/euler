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

from solver.config import html_template, projecteuler_url, resource_dirname, statement_filename, test_cases_filename
from solver.problems import Problem
from solver.results import read_results, solutions_history
from solver.stack import read_stack_file
from solver.utils.download import download_file


def clean_html_for_local(problem_content_obj: BeautifulSoup, *,
                         problem: Problem,
                         problem_url: str,
                         test_cases: str,
                         results: str,
                         solution_notes: str,
                         ) -> str:
    """
    Wrap problem content in a self-contained HTML page suitable for local viewing.

    Embeds basic CSS styles and MathJax scripts for rendering mathematical notation,
    and appends a test cases section (always refreshed) and a solution approach section
    (content preserved from the previous version of the file).

    Args:
        problem_content_obj: Parsed HTML of the problem content div.
        problem:             The Project Euler problem metadata.
        problem_url:         The canonical URL of the problem on projecteuler.net.
        test_cases:          Inner HTML for the test cases section. Defaults to empty.
        results:             Inner HTML for the results section. Defaults to empty.
        solution_notes:      Inner HTML for the solution approach div. Defaults to empty.

    Returns:
        A complete HTML document string.
    """
    content = BeautifulSoup(str(problem_content_obj), 'html.parser')
    html = html_template.substitute(
        title=f'Problem {problem!s}',
        heading=f'Problem {problem!s}',
        problem_url=problem_url,
        content=str(content),
        test_cases=test_cases,
        results=results,
        solution_notes=solution_notes,
    )
    return '\n'.join(line.rstrip() for line in html.splitlines())


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


def get_results_html(problem: Problem) -> str:
    """Render problem results as HTML, aligned with the structure of get_test_cases_html.

    Returns an HTML string with one <h3>/<ul> block.  If the problem has been solved
    (i.e. appears in solutions_history) but no correct main results are recorded,
    a "solution to be restored" notice is included.
    """
    solved_date: str | None = solutions_history().get(problem.number)
    results = read_results(problem.number)
    if not solved_date:
        return '<p><em>Solution pending... the mathematician is still thinking.</em></p>'
    header = f'<h3><strong>First Solved:</strong> {solved_date}</h3>'
    if not results:
        return header + '\n<p><em>Solution to be restored.</em></p>'
    correct = [r for r in results if r.verdict == 'correct']
    args_best_elapsed: dict[str, float] = {}
    for r in correct:
        if r.args not in args_best_elapsed or r.elapsed < args_best_elapsed[r.args]:
            args_best_elapsed[r.args] = r.elapsed
    rows: list[str] = []
    prev_solution: str | None = None
    for r in correct:
        if prev_solution is not None and r.solution != prev_solution:
            rows.append('<tr class="result-spacer"><td colspan="6"></td></tr>')
        prev_solution = r.solution
        answer = r.answer if problem.number <= 100 or r.category == 'dev' else '█'
        row_css = f' class="result-{r.category}"'
        elapsed_flag = ' ⚡' if r.elapsed == args_best_elapsed.get(r.args) else ''
        rows.append(f'<tr{row_css}>'
                    f'<td>{r.category}</td>'
                    f'<td>{r.solution}</td>'
                    f'<td>{r.args}</td>'
                    f'<td>→</td>'
                    f'<td>{answer}</td>'
                    f'<td>{r.elapsed:.3f}s{elapsed_flag}</td>'
                    f'</tr>')
    if not rows:
        return header + '\n<p><em>Solution to be restored.</em></p>'
    return header + '\n<table>\n<tbody>\n' + '\n'.join(rows) + '\n</tbody>\n</table>'


def get_solution_notes_html(problem_number: int) -> str:
    """
    Extract the inner HTML of the solution notes div from the existing HTML stack file.

    Args:
        problem_number: The Project Euler problem number.

    Returns:
        The inner HTML string of the solution notes div, or an empty string if the
        file does not exist or the div is absent.
    """
    notes: str = ''
    try:
        html_bytes: bytes = read_stack_file(problem_number, statement_filename)[0]
        soup: BeautifulSoup = BeautifulSoup(html_bytes.decode(), 'html.parser')
        if div := soup.find('div', id='solution-notes-content'):
            notes = div.decode_contents().strip('\n')
    except FileNotFoundError:
        pass
    return notes or '<p><em>Nothing here yet - come back when the dust has settled.</em></p>'


def get_test_cases_html(problem_number: int, test_cases: list[dict]) -> str:
    """
    Render test cases as HTML sections grouped by category.

    Answers are revealed for problems 1–100 and for 'dev' category test cases;
    all other answers are rendered as '?'.

    Args:
        problem_number: The Project Euler problem number.
        test_cases:     List of test case dicts, each with 'input' and 'category' keys
                        and an optional 'answer' key.

    Returns:
        An HTML string
    """
    sections: dict[str, list[str]] = {}
    for tc in test_cases:
        category: str = tc.get('category', 'extra')
        args: str = ', '.join(f'{k}={v!r}' for k, v in tc['input'].items())
        ans: Any = tc.get('answer')
        answer: str = repr(ans) if ans is not None and (problem_number <= 100 or category == 'dev') else '█'
        sections.setdefault(category, []).append(f'<li><code>{category}: solve({args}) → {answer}</code></li>')
    if not sections:
        return '<p><em>No test cases yet - someone has to go first.</em></p>'
    parts: list[str] = []
    for category, items in sections.items():
        parts.append('<ul>\n' + '\n'.join(items) + '\n</ul>')
    return '\n'.join(parts)


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
    files: dict[str, bytes] = extract_resources(problem_content, force_refresh=force_refresh)
    try:
        test_cases = get_test_cases_html(problem.number, loads(read_stack_file(problem.number, test_cases_filename)[0]))
    except (FileNotFoundError, JSONDecodeError):
        test_cases = ''
    results = get_results_html(problem)
    solution_notes = get_solution_notes_html(problem.number)
    html: str = clean_html_for_local(problem_content, problem=problem, problem_url=problem_url, test_cases=test_cases,
                                     results=results, solution_notes=solution_notes)
    html = BeautifulSoup(html, 'html.parser').prettify()
    files[statement_filename] = html.encode()
    return problem, files


__all__ = ('problem_statement',)
