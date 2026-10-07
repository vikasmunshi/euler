#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The progress page → `problems.json` pipeline, shared by the shell and the web tier.

Two writers produce `problems.json` from a saved projecteuler.net progress page: the
shell's `summary` command (:mod:`solver.core.summary`) and the web tier's upload
(`solver.web.site.content.save_progress`). They used to carry a copy of the parser each,
and the copies had already drifted — the web one wrote the parsed page straight over the
file, un-solving every problem `mark` had recorded ahead of the page.

So this module is **config-free and shell-free**: every function takes text or a path
explicitly, and nothing here imports :mod:`solver.config` or :mod:`solver.shell`. That is
what lets the web service, which may not resolve the shell's identity, import it.
"""
from __future__ import annotations

__all__ = ['ProblemRecord', 'parse_progress', 'read_problems', 'carry_solved', 'write_problems',
           'merge_progress']

from json import JSONDecodeError, dumps, loads
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag

#: One problem's row in `problems.json`: `{title, level, pct, solved, date}` — `level` and
#: `pct` are ints or `''` when unknown, `date` is `''` for an unsolved problem.
ProblemRecord = dict[str, str | int | bool]


def parse_progress(text: str) -> dict[int, ProblemRecord]:
    """Parse a saved projecteuler.net progress page into `{number: record}`.

    Empty when the text holds no problem cells — a missing file, or a paste of the wrong
    page — which both callers treat as "refuse", never as "no problems".
    """
    soup = BeautifulSoup(text, 'html.parser')
    problems: dict[int, ProblemRecord] = {}
    for td in soup.find_all('td', class_='tooltip'):
        a_tag = td.find('a', href=True)
        if not a_tag or not str(a_tag.get('href', '')).startswith('problem='):
            continue
        try:
            num = int(str(a_tag['href']).split('=')[1])
        except (ValueError, IndexError):
            continue
        # Difficulty level from CSS class t_N
        level: int | str = ''
        for cls in (td.get('class') or []):
            if cls.startswith('t_'):
                try:
                    level = int(cls[2:])
                except ValueError:
                    pass
        # Title, percentage, and completion date from tooltip span
        title: str = ''
        pct: int | str = ''
        date: str = ''
        tooltip: Tag | None = a_tag.find('span', class_='tooltiptext_narrow')
        if tooltip:
            for div in tooltip.find_all('div'):
                line: str = div.get_text(strip=True)
                if line.startswith('"') and line.endswith('"'):
                    title = line[1:-1]
                elif 'Difficulty:' in line and '[' in line:
                    try:
                        pct = int(line.split('[')[1].split('%')[0].strip())
                        if level == '' and 'Level' in line:
                            level = int(line.split('Level')[1].split('[')[0].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('Completed on '):
                    date = line[len('Completed on '):]
        solved: bool = 'problem_solved' in (td.get('class') or [])
        problems[num] = {'title': title, 'level': level, 'pct': pct, 'solved': solved, 'date': date}
    return problems


def read_problems(path: Path) -> dict[int, ProblemRecord]:
    """The problems file as it stands now, keyed by number — `{}` when it cannot be read.

    A missing or unparsable file is not an error here: the first import on a fresh clone
    has nothing to compare against, and the write that follows is what creates it. Anything
    unreadable is treated as "nothing recorded" rather than refused, since the parsed page is
    the better of the two states either way.
    """
    try:
        raw: Any = loads(path.read_text(encoding='utf-8'))
    except (OSError, JSONDecodeError, UnicodeDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    recorded: dict[int, ProblemRecord] = {}
    for key, value in raw.items():
        try:
            number = int(key)
        except (TypeError, ValueError):
            continue
        if isinstance(value, dict):
            recorded[number] = value
    return recorded


def carry_solved(problems: dict[int, ProblemRecord], recorded: dict[int, ProblemRecord]) -> list[int]:
    """Keep every `solved` record *recorded* already holds; return the numbers the page denies.

    `solved` is written from two directions and only one of them is the progress page: `mark`
    sets it the moment a problem's own `results.json` confirms the answer, which is *before*
    the answer has been given to projecteuler.net (sometimes long before). A re-import that
    simply overwrote the file would silently un-solve all of those, taking their dates with
    them — so the merge is one-way: a solved record survives a page that does not carry it,
    with its original date, and nothing here ever clears a `solved` flag.

    The numbers returned are exactly the disagreements: solved in the file, not solved on the
    page. Each one means the same thing — the answer was never registered upstream — which is
    worth telling somebody about, because it is the half of solving a problem that the solver
    cannot do for you.
    """
    unregistered: list[int] = []
    for number, was in sorted(recorded.items()):
        if not was.get('solved'):
            continue
        current = problems.get(number)
        if current is None:
            # The page does not carry this problem at all (a partial save, or a problem
            # withdrawn upstream). Carry the whole record over rather than drop a solution.
            problems[number] = dict(was)
        elif not current.get('solved'):
            current['solved'] = True
            current['date'] = was.get('date') or current.get('date', '')
        else:
            continue
        unregistered.append(number)
    return unregistered


def write_problems(path: Path, problems: dict[int, ProblemRecord]) -> None:
    """Write *problems* to *path*, by number — so a carried-over record lands in order."""
    ordered = {number: problems[number] for number in sorted(problems)}
    path.write_text(dumps(ordered, indent=2), encoding='utf-8')


def merge_progress(path: Path, problems: dict[int, ProblemRecord]) -> list[int]:
    """Merge freshly parsed *problems* into the file at *path*; return the unregistered numbers.

    The write is a merge, not a replacement (:func:`carry_solved`), so an import can add
    solved problems but never take one away. Reporting the returned disagreements is the
    caller's: the shell prints them and messages staff, the web tier says so in its status.
    """
    unregistered = carry_solved(problems, read_problems(path))
    write_problems(path, problems)
    return unregistered
