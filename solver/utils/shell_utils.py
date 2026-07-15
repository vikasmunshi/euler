#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utility for running shell commands and capturing their output. """
from __future__ import annotations

__all__ = ['confirm', 'pause', 'run_command']

from pathlib import Path
from subprocess import run

from solver.config import config
from solver.shell import console, register


def confirm(prompt: str) -> bool:
    """Prompt the user for confirmation before proceeding."""
    response = console.input(f'[muted]{prompt}[/muted]\nType "yes" to confirm: ')
    return response.lower() == 'yes'


@register(requires='reader', help_text='Pause for user confirmation to continue.')
def pause() -> int:
    """Pause the program execution until the user presses Enter."""
    console.input('[muted]paused[/muted]\nPress enter to continue: ')
    return 0


def run_command(command: str, *, cwd: Path | None = None, silent: bool = False) -> str | None:
    """Run a shell command and return stripped stdout, or None on non-zero exit."""
    if not silent:
        console.print(f'[muted]> {command}[/muted]')
    result = run(command, shell=True, capture_output=True, text=True, cwd=cwd or config.root_dir)
    if result.returncode == 0:
        return result.stdout.strip()
    if not silent:
        console.print(f'Out:\n{result.stdout}\nErr:\n{result.stderr}\nrc: {result.returncode}',
                      markup=False, highlight=False)
    return None
