#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utility for running shell commands and capturing their output. """
from __future__ import annotations

__all__ = ['pause', 'random', 'run_cmdline', 'run_command', 'sleep']

import time
from datetime import datetime, timedelta
from pathlib import Path
from random import randint
from subprocess import CalledProcessError, DEVNULL, run

from solver.config import ExitCodes, config
from solver.shell import console, dialogue, register


def run_cmdline(cmdline: str) -> int:
    """Run a shell command in the repository root and return its exit code.

    Output is suppressed while the shared console is quiet (a `--silent` command).

    Args:
        cmdline: The shell command string to execute.
    """
    pipe = DEVNULL if console.quiet else None
    try:
        process = run(cmdline, shell=True, check=True, cwd=config.root_dir, stdout=pipe, stderr=pipe, )
    except CalledProcessError as e:
        result: int = e.returncode
    else:
        result = process.returncode
    return result


@register(requires='reader')
def pause(prompt: str = 'paused') -> int:
    """Wait for the user to press Enter before the block carries on.

    A beat in a command block — after a `show`, or between the steps of a walkthrough. With
    nobody to wait for (a pipe, `< /dev/null`, `--silent`) it is a no-op rather than an error,
    so a block that pauses is still scriptable. Leaving the prompt with Ctrl-C or Ctrl-D fails
    the command, so `pause "ready?" || break` stops a loop.

    Args:
        prompt: The line shown above the prompt — what the user is confirming, e.g.
            `pause "registered the answer?"`. Defaults to `paused`.
    """
    dialogue.pause(prompt)
    return ExitCodes.EXIT_OK


@register(requires='reader')
def sleep(seconds: int) -> int:
    """Wait the given number of seconds before the block carries on.

    Blocking, like the shell's `sleep`: the block resumes when the time is up. Says when that
    will be, so a long wait is not mistaken for a hang. Ctrl-C ends it early and fails the
    command, so `sleep {wait} || break` stops a loop.

    Args:
        seconds: How long to wait, in whole seconds; 0 returns at once. Must not be negative.
    """
    if seconds < 0:
        console.print(f'[error]error:[/error] cannot sleep a negative time ({seconds}s)')
        return ExitCodes.EXIT_USAGE
    until: str = (datetime.now() + timedelta(seconds=seconds)).strftime('%H:%M:%S')
    console.print(f'[muted]sleeping {seconds}s, until {until}[/muted]')
    time.sleep(seconds)
    return ExitCodes.EXIT_OK


@register(requires='reader')
def random(max: int = 100, min: int = 1) -> int:
    """Return a random whole number from min to max, both included, as the exit code.

    The number **is** the exit code, which is what an assignment stores — so
    `wait = random 3600 1800` sets `wait` to a number from 1800 to 3600, ready for
    `sleep {wait}`. That also means a result above 0 reads as failure to `&&` / `||`:
    assign it, don't chain on it. (`solver "random"` exits the process with it, which the
    operating system truncates to 0–255.)

    Args:
        max: The largest number it may return. Defaults to 100.
        min: The smallest number it may return. Defaults to 1. Must not exceed *max*.
    """
    if min > max:
        console.print(f'[error]error:[/error] min ({min}) is larger than max ({max})')
        return ExitCodes.EXIT_USAGE
    return randint(min, max)


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
