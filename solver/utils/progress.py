#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Progress: """
from __future__ import annotations

import html as _html
from collections import defaultdict
from datetime import datetime
from json import dumps

from solver.core.config import Config
from solver.core.problems import parse_progress_html
from solver.core.templates import Templates, get_template


# ---------------------------------------------------------------------------
# RdBu_r colour palette (blue = easy / level 0, red = hard / level N-1)
# ---------------------------------------------------------------------------

def _rdbu_r_hex(n_levels: int = 40) -> list[str]:
    """Return n_levels hex colours interpolated from the RdBu_r colour map."""
    # RdBu anchor points: (position_0_to_1, R, G, B)
    anchors: list[tuple[float, int, int, int]] = [
        (0.000, 103, 0, 31),
        (1 / 9, 178, 24, 43),
        (2 / 9, 214, 96, 77),
        (3 / 9, 244, 165, 130),
        (4 / 9, 253, 219, 199),
        (0.500, 247, 247, 247),
        (5 / 9, 209, 229, 240),
        (6 / 9, 146, 197, 222),
        (7 / 9, 67, 147, 195),
        (8 / 9, 33, 102, 172),
        (1.000, 5, 48, 97),
    ]

    def _lerp(t: float) -> str:
        for j in range(len(anchors) - 1):
            p0, r0, g0, b0 = anchors[j]
            p1, r1, g1, b1 = anchors[j + 1]
            if t <= p1 + 1e-9:
                f = (t - p0) / (p1 - p0) if p1 > p0 else 0.0
                r = max(0, min(255, round(r0 + f * (r1 - r0))))
                g = max(0, min(255, round(g0 + f * (g1 - g0))))
                b = max(0, min(255, round(b0 + f * (b1 - b0))))
                return f'#{r:02x}{g:02x}{b:02x}'
        _, r, g, b = anchors[-1]
        return f'#{r:02x}{g:02x}{b:02x}'

    result: list[str] = []
    for i in range(n_levels):
        t = 1.0 - (i / max(n_levels - 1, 1))  # reverse: 0 → blue end, n-1 → red end
        result.append(_lerp(t))
    return result


def _color_vars_css(n_levels: int = 40) -> str:
    """CSS block: :root custom properties + td.problem_solved.t_N rules."""
    colors = _rdbu_r_hex(n_levels)
    lines: list[str] = [':root {']
    for i, c in enumerate(colors):
        lines.append(f'  --t_{i}: {c};')
    lines.append('}')
    lines.append('')
    # Apply background colour to solved cells
    for i in range(n_levels):
        lines.append(f'table.grid td.problem_solved.t_{i} {{ background-color: var(--t_{i}); }}')
    lines.append('')
    # Text contrast: dark text on light backgrounds (approx. levels 9–30)
    lines.append('table.grid td.problem_solved { color: #fff; }')
    dark_text_levels = [
        i for i, c in enumerate(colors)
        if (int(c[1:3], 16) * 299 + int(c[3:5], 16) * 587 + int(c[5:7], 16) * 114) // 1000 > 128
    ]
    if dark_text_levels:
        selectors = ', '.join(f'table.grid td.problem_solved.t_{i}' for i in dark_text_levels)
        lines.append(f'{selectors} {{ color: #1e2030; }}')
    lines.append('')
    # Unsolved cells: faded level colour (35% level + 65% light grey), grey text
    gr, gg, gb = 0xe8, 0xea, 0xef  # base grey #e8eaef
    alpha = 0.35
    for i, c in enumerate(colors):
        r = round(int(c[1:3], 16) * alpha + gr * (1 - alpha))
        g = round(int(c[3:5], 16) * alpha + gg * (1 - alpha))
        b = round(int(c[5:7], 16) * alpha + gb * (1 - alpha))
        faded = f'#{r:02x}{g:02x}{b:02x}'
        lines.append(f'table.grid td.problem_unsolved.t_{i} {{ background-color: {faded}; color: #7a7fa0; }}')
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# HTML generation helpers
# ---------------------------------------------------------------------------

def _cell_html(num: int, info: dict) -> str:
    level = info.get('level', '')
    pct = info.get('pct', '')
    title = _html.escape(info.get('title', ''), quote=True)
    solved = info.get('solved', False)
    status = 'problem_solved' if solved else 'problem_unsolved'
    t_class = f' t_{level}' if level != '' else ''
    href = '/'.join(f'{num:04d}') + '/problem.html'
    return (
        f'<td class="tooltip {status}{t_class}"'
        f' data-num="{num}"'
        f' data-title="{title}"'
        f' data-level="{level}"'
        f' data-pct="{pct}">'
        f'<a href="{href}">{num}</a><span class="tooltiptext_narrow"></span></td>'
    )


def _grids_by_id_html(problems: dict[int, dict]) -> str:
    if not problems:
        return '<p>No problems found in progress.html</p>'
    max_num = max(problems)
    n_grids = (max_num - 1) // 100 + 1
    parts: list[str] = []
    for g in range(n_grids):
        start = g * 100 + 1
        rows: list[str] = []
        solved_in_grid = 0
        total_in_grid = 0
        for row_idx in range(10):
            cells: list[str] = []
            for col_idx in range(10):
                num = start + row_idx * 10 + col_idx
                if num not in problems:
                    cells.append('<td class="empty-cell"></td>')
                    continue
                info = problems[num]
                total_in_grid += 1
                if info.get('solved'):
                    solved_in_grid += 1
                cells.append(_cell_html(num, info))
            rows.append('<tr>' + ''.join(cells) + '</tr>')
        pct = (solved_in_grid / total_in_grid * 100) if total_in_grid else 0.0
        table_html = (
                '<div class="problems_solved_grid">\n'
                f'<table class="grid problems_solved_table" id="grid_{g}">\n'
                + '\n'.join(rows)
                + '\n</table>\n'
                  f'<div class="grid-progress-wrap">'
                  f'<div class="progress_bar"><div class="progress_bar_block" style="width:{pct:.1f}%"></div></div>'
                  f'<span class="grid-caption">Solved {solved_in_grid}&thinsp;/&thinsp;{total_in_grid}</span>'
                  f'</div>\n</div>'
        )
        parts.append(table_html)
    # Group into rows of 3 grids each
    rows_html: list[str] = []
    for i in range(0, len(parts), 3):
        chunk = parts[i:i + 3]
        rows_html.append(
            '<div class="grids-row-layout">\n'
            + '\n'.join(chunk)
            + '\n</div>'
        )
    return '\n'.join(rows_html)


def _levels_grid_html(problems: dict[int, dict]) -> str:
    if not problems:
        return '<p>No problems found in progress.html</p>'
    by_level: dict[int, list[int]] = defaultdict(list)
    for num in sorted(problems):
        level = problems[num].get('level', '')
        if level != '':
            by_level[int(level)].append(num)
    if not by_level:
        return '<p>No difficulty data available.</p>'
    rows: list[str] = []
    for level in sorted(by_level, reverse=True):
        cells = [f'<td class="level">{level}</td>']
        for num in by_level[level]:
            cells.append(_cell_html(num, problems[num]))
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    return (
            '<div class="problems_solved_grid">\n'
            '<table class="grid problems_solved_table" id="grid_levels">\n'
            + '\n'.join(rows)
            + '\n</table>\n</div>'
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def solutions_summary() -> None:
    problems = parse_progress_html()
    if not problems:
        raise ValueError(f'No problems found — is {Config.solutions_progress_file} present?')

    history = {str(num): info['date'] for num, info in problems.items() if info.get('date')}
    solved_count = sum(1 for info in problems.values() if info.get('solved'))
    total_count = len(problems)
    generated_at = datetime.now().strftime('%a, %d %b %Y, %H:%M')

    summary: str = get_template(Templates.INDEX).substitute(
        history=dumps(history, indent=2, sort_keys=True),
        color_vars=_color_vars_css(40),
        grids_by_id=_grids_by_id_html(problems),
        # levels_grid=_levels_grid_html(problems),
        generated_at=generated_at,
        solved_count=str(solved_count),
        total_count=str(total_count),
    )
    Config.solutions_summary_file.write_text(summary)


__all__ = ('solutions_summary',)

if __name__ == '__main__':
    solutions_summary()
