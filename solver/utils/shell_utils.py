#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utility for running shell commands and capturing their output. """
from __future__ import annotations

from pathlib import Path
from readline import get_current_history_length, remove_history_item
from subprocess import run

from solver.core.config import Config


def confirm(prompt: str) -> bool:
    """Prompt the user for confirmation before proceeding."""
    response = input(f'{prompt}\nType "yes" to confirm: ')
    if response:
        remove_history_item(get_current_history_length() - 1)
    return response.lower() == 'yes'


def pause() -> None:
    """Pause the program execution until the user presses Enter."""
    response = input('press enter to continue:')
    if response:
        remove_history_item(get_current_history_length() - 1)
    return None


def run_command(command: str, *, cwd: Path | None = None, silent: bool = False) -> str | None:
    """Run a shell command and return stripped stdout, or None on non-zero exit."""
    if not silent:
        print(f'> {command}')
    result = run(command, shell=True, capture_output=True, text=True, cwd=cwd or Config.root_dir)
    if result.returncode == 0:
        return result.stdout.strip()
    if not silent:
        print(f'Out:\n{result.stdout}\nErr:\n{result.stderr}\nrc: {result.returncode}')
    return None


__all__ = (
    'confirm',
    'pause',
    'run_command',
)
