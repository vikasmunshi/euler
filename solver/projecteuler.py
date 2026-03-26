#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Project Euler problem initialization and content parsing."""
from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from itertools import chain
from pathlib import Path
from re import sub as re_sub
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from solver.download import download_file
from solver.workspace import problems_list_url, projecteuler_url, stack_dir, workspace_dir, write_file

__all__ = ['ProjectEulerFiles', 'init_from_projecteuler', 'problem_numbers']


# ============================================================================
# Enums and Constants
# ============================================================================

class ProjectEulerFiles(StrEnum):
    """Project Euler workspace file names."""

    problem_number_file = 'number.txt'
    problem_statement_html_file = 'problem-statement.html'
    problem_statement_md_file = 'problem-statement.md'
    resources_dir = 'resources'

    @property
    def path(self) -> Path:
        """Get the full path for this file in the workspace."""
        return workspace_dir / self.value

    def stack_path(self, problem_number: int) -> Path:
        """Get the full path for this file in the stack."""
        return stack_dir.joinpath(*f'{problem_number:04d}') / self.value

    @classmethod
    def current_problem_number(cls) -> int | None:
        """Get the current problem number from workspace.

        Returns:
            Problem number or None if not found or invalid
        """
        try:
            return int(cls.problem_number_file.path.read_bytes())
        except (FileNotFoundError, ValueError):
            return None

    @classmethod
    def is_private(cls, problem_number: int | None = None) -> bool | None:
        """ Check if a problem number indicates a private problem (number > 100).

        Args:
            problem_number (Optional[int]): Problem number to check. 
                Uses current problem number if None.

        Returns:
            Optional[bool]: True if private, False if public, None if no valid problem number.
        """
        problem_number = problem_number or cls.current_problem_number()
        if problem_number is None:
            return None
        return problem_number > 100


# ============================================================================
# Problem Initialization
# ============================================================================

def init_from_projecteuler(problem_number: int, force_refresh: bool = False) -> None:
    """Initialize the workspace with a Project Euler problem.

    Downloads the problem statement, parses HTML/Markdown, and downloads resources.

    Args:
        problem_number: Problem number to initialize
        force_refresh: Force re-download even if cached
    """
    if (current := ProjectEulerFiles.current_problem_number()) and current != problem_number:
        print(f'Workspace already exists for problem {current}, clear before initializing {problem_number}')
        return
    if (problem_title := problem_numbers(check_last_modified=False).get(problem_number)) is None:
        print(f'Error: Problem {problem_number} not found in Project Euler list of problems.')
        return
    problem_url: str = urljoin(projecteuler_url, f'problem={problem_number}')
    if (problem_html := download_file(problem_url, refresh=force_refresh, verbose=True)) is None:
        return
    print(f'Initializing workspace for "{problem_number:04d} {problem_title}" from {problem_url}')
    try:
        html_str, md_str = _parse_html(problem_html, problem_number, problem_title, force_refresh)
    except Exception as e:
        print(f'Error: Failed to parse problem {problem_number}: {e}')
        return
    write_file(ProjectEulerFiles.problem_number_file.path, str(problem_number).encode(), verbose=True)
    write_file(ProjectEulerFiles.problem_statement_html_file.path, html_str.encode(), verbose=True)
    write_file(ProjectEulerFiles.problem_statement_md_file.path, md_str.encode(), verbose=True)
    print(f'Workspace initialized for problem {problem_number}.')


@lru_cache(maxsize=2)
def problem_numbers(check_last_modified: bool = True) -> dict[int, str]:
    """Get mapping of problem numbers to titles.

    Args:
        check_last_modified: Check if a cached list is outdated

    Returns:
        Dict mapping problem number to title
    """
    content: bytes | None = download_file(problems_list_url, check_last_modified=check_last_modified)
    if content is None:
        print('Error: Failed to download problem list from Project Euler')
        return {}
    result = {}
    for line in content.strip().splitlines()[1:]:
        if not line:
            continue
        parts = line.split(b'##')
        if len(parts) >= 2:
            result[int(parts[0])] = parts[1].decode('utf-8')
    return result


# ============================================================================
# HTML Parsing (Private)
# ============================================================================

def _clean_html_for_local(problem_content_obj: BeautifulSoup, *,
                          problem_number: int,
                          problem_title: str,
                          difficulty_level: str,
                          ) -> str:
    """Create a standalone HTML file with styling and MathJax.

    Args:
        problem_content_obj: BeautifulSoup problem content object
        problem_number: Problem number
        problem_title: Problem title
        difficulty_level: Problem difficulty level

    Returns:
        Complete HTML document as a string
    """
    content = BeautifulSoup(str(problem_content_obj), 'html.parser')
    return (
        '<!DOCTYPE html>\n'
        '<html>\n'
        '<head>\n'
        '    <meta charset="UTF-8">\n'
        f'    <title>{problem_number} - {problem_title}</title>\n'
        '    <style>\n'
        '        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }\n'
        '        .problem_content { line-height: 1.6; }\n'
        '        var { font-style: italic; }\n'
        '        sup { vertical-align: super; font-size: smaller; }\n'
        '        sub { vertical-align: sub; font-size: smaller; }\n'
        '        img { max-width: 100%; height: auto; }\n'
        '        table { border-collapse: collapse; margin: 20px 0; }\n'
        '        td, th { border: 1px solid #ddd; padding: 8px; }\n'
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
        f'    <h1>{problem_number} - {problem_title} (level {difficulty_level})</h1>\n'
        f'    {content}\n'
        '</body>\n'
        '</html>'
    )


def _html_to_markdown(problem_content_obj: BeautifulSoup, *,
                      problem_number: int,
                      problem_title: str,
                      difficulty_level: str,
                      ) -> str:
    """Convert HTML problem content to Markdown.

    Args:
        problem_content_obj: BeautifulSoup problem content object
        problem_number: Problem number
        problem_title: Problem title
        difficulty_level: Problem difficulty level

    Returns:
        Markdown formatted string
    """
    content: BeautifulSoup
    table: BeautifulSoup

    content = BeautifulSoup(str(problem_content_obj), 'html.parser')
    for table in content.find_all('table'): # type: ignore [assignment]
        md_table = _table_to_markdown(table)
        table.replace_with(md_table)
    for math_tag in content.find_all(['math', 'span'], class_=lambda x: x and 'math' in x):
        math_tag.replace_with(f'$${math_tag.get_text()}$$')
    for tag in content.find_all('var'):
        tag.replace_with(f'*{tag.get_text()}*')
    for tag in content.find_all('dfn'):
        tag.replace_with(f'**{tag.get_text()}**')
    for tag in content.find_all('b'):
        tag.replace_with(f'**{tag.get_text()}**')
    for tag in content.find_all('i'):
        tag.replace_with(f'*{tag.get_text()}*')
    for sup in content.find_all('sup'):
        text: str = sup.get_text()
        sup.replace_with(f'<sup>{text}</sup>')
    for sub in content.find_all('sub'):
        text = sub.get_text()
        sub.replace_with(f'<sub>{text}</sub>')
    for a in content.find_all('a'):
        href: str = a.get('href', '')  # type: ignore [assignment]
        text = a.get_text()
        if href.startswith(ProjectEulerFiles.resources_dir):
            a.replace_with(f'[{text}]({href})')
        else:
            a.replace_with(text)
    for img in content.find_all('img'):
        src: str = img.get('src', '')  # type: ignore [assignment]
        alt: str = img.get('alt', 'image')  # type: ignore [assignment]
        img.replace_with(f'![{alt}]({src})')
    for p in content.find_all('p'):
        p.insert_after('\n\n')
    md_text = content.get_text()
    md_text = re_sub(r'\n{4,}', '\n\n', md_text)
    md_text = md_text.strip()
    return f'# {problem_number} - {problem_title} (level {difficulty_level})\n\n{md_text}'


def _parse_html(problem_html: bytes,
                problem_number: int,
                problem_title: str,
                force_refresh: bool, ) -> tuple[str, str]:
    """Parse problem HTML and download resources.

    Args:
        problem_html: Raw HTML bytes
        problem_number: Problem number
        problem_title: Problem title
        force_refresh: Force re-download of resources

    Returns:
        Tuple of (HTML string, Markdown string)
    """
    problem_soup: BeautifulSoup
    problem_content_obj: BeautifulSoup
    src: str
    difficulty_level: str
    attr: str
    html_str: str
    md_str: str

    problem_soup = BeautifulSoup(problem_html, 'html.parser')
    difficulty_level = '??'
    if (tooltip := problem_soup.find('span', class_='tooltiptext_right')) and (text := tooltip.get_text()):
        for line in text.split(';'):
            if 'Difficulty level:' in line:
                difficulty_level = line.split(':')[-1].strip()
                break
        else:
            difficulty_level = '--'
    problem_content_obj = problem_soup.find('div', {'class': 'problem_content'})  # type: ignore [assignment]
    if not problem_content_obj:
        raise ValueError(f'Problem {problem_number}: Could not find problem_content div in HTML')
    for element in chain(problem_content_obj.find_all('a'), problem_content_obj.find_all('img')):
        attr = {'a': 'href', 'img': 'src'}[element.name]
        if ((src := element.get(attr, ''))  # type: ignore [assignment]
                and (src.startswith('resources/') or src.startswith('project/images/'))):
            url: str = urljoin(projecteuler_url, src)
            local_filename: str = f'{ProjectEulerFiles.resources_dir}/{src.split("/")[-1].split("?")[0]}'
            if (content := download_file(url, refresh=force_refresh, verbose=True)) is None:
                print(f'Error: Failed to download {local_filename} from {url}')
                continue
            write_file(workspace_dir / local_filename, content, verbose=True)
            element[attr] = local_filename
    html_str = _clean_html_for_local(problem_content_obj,
                                     problem_number=problem_number,
                                     problem_title=problem_title,
                                     difficulty_level=difficulty_level)
    md_str = _html_to_markdown(problem_content_obj,
                               problem_number=problem_number,
                               problem_title=problem_title,
                               difficulty_level=difficulty_level)
    return html_str, md_str


def _table_to_markdown(table: BeautifulSoup) -> str:
    """Convert HTML table to Markdown format.

    Args:
        table: BeautifulSoup table object

    Returns:
        Markdown formatted table string
    """
    rows = []
    for tr in table.find_all('tr'):
        cells = []
        for cell in tr.find_all(['td', 'th']):
            # Get cell text and strip whitespace
            cell_text = cell.get_text().strip()
            cells.append(cell_text)
        if cells:
            rows.append(cells)
    if not rows:
        return ''
    md_lines = []
    if rows:
        md_lines.append('| ' + ' | '.join(rows[0]) + ' |')
        md_lines.append('| ' + ' | '.join(['---'] * len(rows[0])) + ' |')
        for row in rows[1:]:
            while len(row) < len(rows[0]):
                row.append('')
            md_lines.append('| ' + ' | '.join(row) + ' |')
    return '\n' + '\n'.join(md_lines) + '\n'
