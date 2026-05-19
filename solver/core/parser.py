#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Project Euler scraper: fetches problem pages and builds standalone HTML with test cases and solution approach."""
from __future__ import annotations

from itertools import chain
from json import JSONDecodeError, loads
from os.path import dirname, relpath
from re import DOTALL, sub
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from bs4.element import AttributeValueList

from solver.core.config import config
from solver.core.problems import Problem, problems
from solver.core.problems import solutions_history
from solver.core.results import FormattedResult, Result, read_results
from solver.core.notes import get_solution_notes_html
from solver.core.stack import read_stack_file, stack_base_dir
from solver.core.templates import Templates, get_template
from solver.core.console import console
from solver.utils.download import download_file
from solver.utils.path_utils import canonical_path


def clean_html_for_local(*,
                         content: str,
                         euler_url: str,
                         github_url: str,
                         next_url: str,
                         previous_url: str,
                         problem: Problem,
                         solution_notes: str,
                         solved_results: str,
                         test_cases: str,
                         ) -> bytes:
    """
    Wrap problem content in a self-contained HTML page suitable for local viewing.

    Embeds basic CSS styles and MathJax scripts for rendering mathematical notation
    and appends a test cases section (always refreshed) and a solution approach section
    (content preserved from the previous version of the file).

    Args:
        content:                The Parsed HTML of the problem content div.
        euler_url:              The URL of the problem on projecteuler.net.
        github_url:             The URL of the problem on GitHub.
        next_url:               The canonical URL of the next problem.
        previous_url:           The canonical URL of the previous problem.
        problem:                The Project Euler problem metadata.
        solved_results:                Inner HTML for the results section. Defaults to empty.
        solution_notes:         Inner HTML for the solution approach div. Defaults to empty.
        test_cases:             Inner HTML for the test cases section. Defaults to empty.

    Returns:
        A complete HTML document string.
    """
    html: str = get_template(Templates.PROBLEM).substitute(
        content=content,
        euler_url=euler_url,
        github_url=github_url,
        next_url=next_url,
        previous_url=previous_url,
        results=solved_results,
        solution_notes=solution_notes,
        test_cases=test_cases,
        title=problem.as_title(),
    )
    html = '\n'.join(line.rstrip() for line in html.splitlines())
    prettified: str = BeautifulSoup(html, 'html.parser').prettify()
    # prettify() expands <code>content</code> to three lines with indentation; undo that.
    # Group 1: rest of the line before <code> (e.g. "<li>" or "filtering by").
    # Group 2: content inside <code>, with surrounding whitespace stripped.
    # Group 3: rest of the line after </code> (e.g. "</li>" or ",").
    # A space is inserted before <code> unless group 1 ends with ">" (tag boundary),
    # and after </code> unless group 3 starts with "<" or punctuation.
    prettified = sub(
        r'([^\n]*)\n\s*<code>\n\s*(.*?)\n\s*</code>\n\s*([^\n]*)',
        lambda m: (m.group(1) + ('' if m.group(1).endswith('>') else ' ')
                   + f'<code>{m.group(2)}</code>'
                   + ('' if m.group(3)[:1] in '<,.:;)!?' else ' ') + m.group(3)),
        prettified, flags=DOTALL,
    )
    return prettified.encode('utf-8')


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


def get_results_html(problem: Problem, test_cases: list[dict[str, Any]]) -> str:
    """Render problem results as HTML, aligned with the structure of get_test_cases_html.

    Returns an HTML string with one <h3>/<ul> block.  If the problem has been solved
    (i.e. appears in solutions_history) but no correct main results are recorded,
    a "solution to be restored" notice is included.
    """
    solved_date: str | None = solutions_history.get(problem.number)
    solved_results: list[Result] = read_results(problem.number)
    if not solved_date:
        return f'<p><em>{config.default_results}</em></p>'
    header: str = f'<h4>First Solved: {solved_date}</h4>'
    if not solved_results:
        return header + '\n<p><em>Solution vanished into the void. Send search party.</em></p>'
    correct: list[FormattedResult] = [r.formatted() for r in solved_results if r.verdict == 'correct']
    test_cases_order: dict[str, int] = {' '.join(map(str, tc['input'].values())): i for i, tc in enumerate(test_cases)}
    correct = sorted(correct, key=lambda r: (test_cases_order[r.args], r.lang, r.filename))
    num_solutions: int = len(set(r.filename for r in correct))
    if not correct:
        return header + '\n<p><em>Solution exists, correctness... debatable.</em></p>'
    args_best_elapsed: dict[str, float] = {}
    for r in correct:
        if r.args not in args_best_elapsed or r.average < args_best_elapsed[r.args]:
            args_best_elapsed[r.args] = r.average
    rows: list[str] = []
    prev_group: tuple[str, str] | None = None
    for r in correct:
        this_group: tuple[str, str] = (r.args, r.lang if num_solutions > 1 else '')
        if prev_group is not None and this_group != prev_group:
            rows.append('<tr class="result-spacer"><td colspan="6"></td></tr>')
        prev_group = this_group
        answer = r.answer if problem.number <= 100 or r.category == 'dev' else '█'
        row_css = f' class="result-{r.category}"'
        elapsed_flag = ' ⚡' if r.average == args_best_elapsed.get(r.args) else ''
        rows.append(f'<tr{row_css}>'
                    f'<td>{r.category}</td>'
                    f'<td>{r.solution_href}</td>'
                    f'<td>{r.args_short}</td>'
                    f'<td>→</td>'
                    f'<td>{answer}</td>'
                    f'<td>{r.average:.9f}s{elapsed_flag}</td>'
                    f'</tr>')
    if not rows:
        return header + '\n<p><em>Solution to be restored.</em></p>'
    return header + '\n<table>\n<tbody>\n' + '\n'.join(rows) + '\n</tbody>\n</table>'


def get_test_cases_html(problem_number: int, test_cases: list[dict[str, Any]]) -> str:
    """ Render test cases as HTML sections grouped by category. """
    if not test_cases:
        return f'<p><em>{config.default_test_cases}</em></p>'
    sections: dict[str, list[str]] = {}
    for tc in test_cases:
        category: str = tc['category']
        if 'file_url' in tc['input']:
            tc['input']['file_url'] = tc['input']['file_url'].split('/')[-1]
        args: str = ', '.join(f'{k}={v!r}' for k, v in tc['input'].items())
        ans: Any = tc['answer']
        answer: str = repr(ans) if ans is not None and (problem_number <= 100 or category == 'dev') else '█'
        sections.setdefault(category, []).append(f'<li><code>{category}: solve({args}) → {answer}</code></li>')
    parts: list[str] = [f'<ul>\n{'\n'.join(items)}\n</ul>' for category, items in sections.items()]
    if not parts:
        return f'<p><em>{config.default_test_cases}</em></p>'
    return '\n'.join(parts)


def problem_nav_urls(problem_number: int, /) -> tuple[str, str, str]:
    """Return the canonical and relative navigation URLs for a problem's HTML page.

    Args:
        problem_number: The Project Euler problem number.

    Returns:
        A 3-tuple of "(this_url, next_url, previous_url)" where "this_url"
        is the canonical path to the current problem's directory (used as the
        base for GitHub links and asset paths), and "next_url" / "previous_url"
        are paths relative to that directory pointing to the adjacent problems'
        "problem.html" files (suitable for use as "href" values in the page).
        Navigation wraps around: problem 1's previous is the last problem, and
        the last problem's next is problem 1.
    """
    max_problem_number: int = problems[-1].number
    this_url: str = canonical_path(stack_base_dir(problem_number)) + '/'
    next_problem: int = (problem_number % max_problem_number) + 1
    previous_problem: int = ((problem_number - 2) % max_problem_number) + 1
    next_url: str = canonical_path(stack_base_dir(next_problem)) + '/problem.html'
    previous_url: str = canonical_path(stack_base_dir(previous_problem)) + '/problem.html'
    this_dir: str = dirname(this_url)
    next_url = relpath(next_url, this_dir)
    previous_url = relpath(previous_url, this_dir)
    return this_url, next_url, previous_url


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
    this_url, next_url, previous_url = problem_nav_urls(problem_number)
    euler_url: str = urljoin(config.projecteuler_url, f'problem={problem.number}')
    github_url: str = f'{config.project_git_url}/blob/master/{this_url}'
    if (problem_html := download_file(euler_url, refresh=force_refresh)) is None:
        raise ValueError(f'Problem {problem.number}: Failed to download HTML from {euler_url}')
    problem_soup: BeautifulSoup = BeautifulSoup(problem_html, 'html.parser')
    content: BeautifulSoup = problem_soup.find('div', {'class': 'problem_content'})  # type: ignore [assignment]
    if not content:
        raise ValueError(f'Problem {problem.number}: Could not find problem_content div in HTML')
    files: dict[str, bytes] = extract_resources(content, force_refresh=force_refresh)
    try:
        test_cases: list[dict[str, Any]] = loads(read_stack_file(problem_number, config.test_cases_filename)[0])
    except (FileNotFoundError, JSONDecodeError):
        test_cases = []
    solved_results: str = get_results_html(problem, test_cases)
    solution_notes: str = get_solution_notes_html(problem.number)
    test_cases_html: str = get_test_cases_html(problem.number, test_cases)
    html: bytes = clean_html_for_local(content=str(content),
                                       euler_url=euler_url,
                                       github_url=github_url,
                                       next_url=next_url,
                                       previous_url=previous_url,
                                       problem=problem,
                                       solved_results=solved_results,
                                       solution_notes=solution_notes,
                                       test_cases=test_cases_html, )
    files[config.statement_filename] = html
    return problem, files


__all__ = ('problem_statement',)
