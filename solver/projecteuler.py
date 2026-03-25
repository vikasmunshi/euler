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
from solver.workspace import PROBLEMS_LIST_URL, PROJECTEULER_URL, STACK_DIR, WORKSPACE_DIR, write_file

__all__ = ['ProjectEulerFiles', 'init_from_projecteuler', 'problem_numbers']


# ============================================================================
# Enums and Constants
# ============================================================================

class ProjectEulerFiles(StrEnum):
    """Project Euler workspace file names."""

    problem_number_file = 'number.txt'
    difficulty_level_file = 'level.txt'
    problem_resources_dir = 'resources'
    problem_statement_html_file = 'problem.html'
    problem_statement_md_file = 'problem.md'
    problem_title_file = 'title.txt'
    problem_url_file = 'url.txt'

    @property
    def path(self) -> Path:
        """Get the full path for this file in the workspace."""
        return WORKSPACE_DIR / self.value

    def stack_path(self, problem_number: int) -> Path:
        """Get the full path for this file in the stack."""
        return STACK_DIR.joinpath(*f'{problem_number:04d}') / self.value

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
    def current_difficulty_level(cls) -> int | None:
        """Get the current problem's difficulty level from workspace.

        Returns:
            Difficulty level or None if not found or invalid
        """
        try:
            return int(cls.difficulty_level_file.path.read_bytes())
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
    problem_url: str = urljoin(PROJECTEULER_URL, f'problem={problem_number}')
    if (problem_html := download_file(problem_url, refresh=force_refresh, verbose=True)) is None:
        return
    print(f'Initializing workspace for "{problem_number:04d} {problem_title}" from {problem_url}')
    try:
        difficulty_level = _extract_difficulty_level(problem_html)
        html_str, md_str = _parse_html(problem_html, problem_number, problem_title, force_refresh)
    except Exception as e:
        print(f'Error: Failed to parse problem {problem_number}: {e}')
        return
    write_file(ProjectEulerFiles.problem_number_file.path, str(problem_number).encode(), verbose=True)
    write_file(ProjectEulerFiles.difficulty_level_file.path, str(difficulty_level).encode(), verbose=True)
    write_file(ProjectEulerFiles.problem_statement_html_file.path, html_str.encode(), verbose=True)
    write_file(ProjectEulerFiles.problem_statement_md_file.path, md_str.encode(), verbose=True)
    write_file(ProjectEulerFiles.problem_title_file.path, problem_title.encode(), verbose=True)
    write_file(ProjectEulerFiles.problem_url_file.path, problem_url.encode(), verbose=True)
    print(f'Workspace initialized for problem {problem_number}.')


@lru_cache(maxsize=2)
def problem_numbers(check_last_modified: bool = True) -> dict[int, str]:
    """Get mapping of problem numbers to titles.

    Args:
        check_last_modified: Check if a cached list is outdated

    Returns:
        Dict mapping problem number to title
    """
    content: bytes = download_file(PROBLEMS_LIST_URL, check_last_modified=check_last_modified)
    if not content:
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

def _extract_difficulty_level(problem_html: bytes) -> int | None:
    """Extract difficulty level from problem HTML.

    Args:
        problem_html: Raw HTML bytes

    Returns:
        Difficulty level as integer (defaults to 0 if not found)
    """
    soup = BeautifulSoup(problem_html, 'html.parser')
    tooltip = soup.find('span', class_='tooltiptext_right')
    if tooltip and (text := tooltip.get_text()):
        for line in text.split(';'):
            if 'Difficulty level:' in line:
                try:
                    return int(line.split('Difficulty level:')[-1].strip())
                except (ValueError, IndexError):
                    pass
    return None


def _clean_html_for_local(problem_content_obj, title: str) -> str:
    """Create a standalone HTML file with styling and MathJax.

    Args:
        problem_content_obj: BeautifulSoup problem content object
        title: Problem title

    Returns:
        Complete HTML document as a string
    """
    content = BeautifulSoup(str(problem_content_obj), 'html.parser')
    return (
        '<!DOCTYPE html>\n'
        '<html>\n'
        '<head>\n'
        '    <meta charset="UTF-8">\n'
        f'    <title>{title}</title>\n'
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
        f'    <h1>{title}</h1>\n'
        f'    {content}\n'
        '</body>\n'
        '</html>'
    )


def _html_to_markdown(problem_content_obj, title: str) -> str:
    """Convert HTML problem content to Markdown.

    Args:
        problem_content_obj: BeautifulSoup problem content object
        title: Problem title

    Returns:
        Markdown formatted string
    """
    content = BeautifulSoup(str(problem_content_obj), 'html.parser')
    for table in content.find_all('table'):
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
        text = sup.get_text()
        sup.replace_with(f'<sup>{text}</sup>')
    for sub in content.find_all('sub'):
        text = sub.get_text()
        sub.replace_with(f'<sub>{text}</sub>')
    for a in content.find_all('a'):
        href = a.get('href', '')
        text = a.get_text()
        if href.startswith(ProjectEulerFiles.problem_resources_dir):
            a.replace_with(f'[{text}]({href})')
        else:
            a.replace_with(text)
    for img in content.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', 'image')
        img.replace_with(f'![{alt}]({src})')
    for p in content.find_all('p'):
        p.insert_after('\n\n')
    md_text = content.get_text()
    md_text = re_sub(r'\n{4,}', '\n\n', md_text)
    md_text = md_text.strip()
    return f'# {title}\n\n{md_text}'


def _parse_html(problem_html: bytes, problem_number: int, problem_title: str, force_refresh: bool) -> tuple[str, str]:
    """Parse problem HTML and download resources.

    Args:
        problem_html: Raw HTML bytes
        problem_number: Problem number
        problem_title: Problem title
        force_refresh: Force re-download of resources

    Returns:
        Tuple of (HTML string, Markdown string)
    """
    problem_soup: BeautifulSoup = BeautifulSoup(problem_html, 'html.parser')
    problem_content_obj: BeautifulSoup = problem_soup.find('div', {'class': 'problem_content'})
    if not problem_content_obj:
        raise ValueError(f'Problem {problem_number}: Could not find problem_content div in HTML')
    for element in chain(problem_content_obj.find_all('a'), problem_content_obj.find_all('img')):
        attr: str = {'a': 'href', 'img': 'src'}[element.name]
        if (src := element.get(attr, '')) and (src.startswith('resources/') or src.startswith('project/images/')):
            url: str = urljoin(PROJECTEULER_URL, src)
            local_filename: str = f'{ProjectEulerFiles.problem_resources_dir}/{src.split("/")[-1].split("?")[0]}'
            if (content := download_file(url, refresh=force_refresh, verbose=True)) is None:
                print(f'Error: Failed to download {local_filename} from {url}')
                continue
            write_file(WORKSPACE_DIR / local_filename, content, verbose=True)
            element[attr] = local_filename
    html_str = _clean_html_for_local(problem_content_obj, problem_title)
    md_str = _html_to_markdown(problem_content_obj, problem_title)
    return html_str, md_str


def _table_to_markdown(table) -> str:
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
