#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""List solution directory contents."""
from __future__ import annotations

import datetime
import mimetypes

from solver.config import ExitCodes
from solver.core.problems import Problem
from solver.shell import console, register
from solver.utils.path_utils import canonical_path, iterdir_recursive


@register(requires='reader', help_text='List the solutions dir for given/current problem.', quietable=True)
def ls(problem: Problem) -> int:
    """This function lists all files found recursively in the solution directory of a
    given problem while displaying their canonical paths and file sizes. The files
    are shown in sorted order for easy navigation.

    Args:
        problem (Problem): The problem instance containing the solution directory.
    """
    solution_prefix: str = f'p{problem.number:04d}_s'
    files: list[tuple[str, int, float, str, bool]] = [
        (canonical_path(file), f_stat.st_size, f_stat.st_ctime, mimetype, file.name.startswith(solution_prefix))
        for file in sorted(iterdir_recursive(problem.solution_dir, rt='path'))
        if (mimetype := mimetypes.guess_type(file.name)[0]) is not None  # hides files without an extension
        if (f_stat := file.stat())
    ]
    if not files:
        console.print('[error]error:[/error] no files found in the solution directory')
        return ExitCodes.EXIT_ERROR
    max_filename_length: int = max(len(fileinfo[0]) for fileinfo in files)
    for filename, size, mtime, mimetype, is_a_solution in files:
        mark = ' [accent]*[/accent]' if is_a_solution else ''
        modified: str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        console.print(f'{filename:<{max_filename_length}} {size:6d} bytes {modified} {mimetype}{mark}', highlight=True)
    return ExitCodes.EXIT_OK
