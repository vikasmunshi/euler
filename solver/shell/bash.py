#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
The `!` (`sh` / `bash`) built-in command: run a bash command in the current
problem's solution directory.

Interactive subshells (`sh`/`bash`, `py`, `claude`) take over the terminal
directly; every other command streams its combined output through
`sys.stdout` so the shell's session-log tee can capture it.
"""
from __future__ import annotations

__all__ = []

import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Protocol

from prompt_toolkit.completion import Completion

from solver.config import ExitCodes, config
from solver.shell.command import Context, command


def _bash_completer(ctx: Context, incomplete: str) -> Iterable[str | Completion]:
    """Completer for the `!` / `bash` / `sh` shell-passthrough command.

    * First positional token (the shell command itself): list executable
      files found in `/bin`, `/usr/bin`, `/usr/local/bin`, `~/local/bin`,
      and `~/.local/bin` (deduplicated, first occurrence wins).
    * Subsequent tokens: try the command's own completions via
      `bash -c "compgen ..."`; merge with the solution directory's files.
    """
    # Count completed positional tokens already on the line.
    # When *incomplete* is non-empty it is the last entry of `ctx.argv`,
    # which we don't want to count as "already supplied".
    pos_count = len(ctx.argv) - (1 if incomplete else 0)
    if pos_count <= 0:
        # Complete a shell command name from well-known bin dirs.
        seen: set[str] = set()
        results: list[str] = []
        bin_dirs = (
            '/bin',
            '/usr/bin',
            '/usr/local/bin',
            os.path.expanduser('~/local/bin'),
            os.path.expanduser('~/.local/bin'),
        )
        for d in bin_dirs:
            try:
                entries = os.listdir(d)
            except OSError:
                continue
            for entry in entries:
                if entry in seen or not entry.startswith(incomplete):
                    continue
                full = os.path.join(d, entry)
                if os.access(full, os.X_OK) and os.path.isfile(full):
                    seen.add(entry)
                    results.append(entry)
        results.sort()
        return results
    # Subsequent tokens: command-specific completions + solution-directory files.
    results = []
    seen = set()
    # Build the full bash command line so multi-level completions work, e.g.
    # `git checkout <branch>` rather than only `git <subcommand>`.  When
    # *incomplete* is empty (the line ends with a space) the current word being
    # completed is an empty trailing token.
    words = list(ctx.argv) if incomplete else [*ctx.argv, '']
    cword = len(words) - 1
    cmd_name = words[0]
    cur = words[cword]
    prev = words[cword - 1] if cword > 0 else ''
    comp_line = ' '.join(words)
    # Ask bash for command-specific completions via compgen.
    try:
        q_cmd = shlex.quote(cmd_name)
        q_inc = shlex.quote(incomplete)
        q_words = ' '.join(shlex.quote(w) for w in words)
        script = (
            '{ '
            'source /etc/bash_completion; '
            'source ~/.bash_completion; '
            f'declare -F _completion_loader >/dev/null && _completion_loader {q_cmd}; '
            '} >/dev/null 2>&1; '
            # Extract the real completion function registered for the command.
            f'_fn=$(complete -p {q_cmd} 2>/dev/null | sed -n "s/.*-F \\([^ ]*\\).*/\\1/p"); '
            f'if [ -n "$_fn" ]; then COMP_WORDS=({q_words}); COMP_CWORD={cword}; '
            f'COMP_LINE={shlex.quote(comp_line)}; COMP_POINT=${{#COMP_LINE}}; '
            f'"$_fn" {q_cmd} {shlex.quote(cur)} {shlex.quote(prev)} 2>/dev/null; '
            f'printf "%s\\n" "${{COMPREPLY[@]}}"; fi; '
            f'compgen -o default -- {q_inc} 2>/dev/null'
        )
        proc = subprocess.run(
            ['bash', '-c', script],
            capture_output=True, text=True, timeout=2, cwd=ctx.variables.problem.solution_dir, check=False,
        )
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                results.append(line)
    except (OSError, subprocess.TimeoutExpired):
        pass
    # Solution-directory files as a fallback / supplement.
    try:
        for f in sorted(ctx.variables.problem.solution_dir.iterdir()):
            if f.name.startswith(incomplete) and f.name not in seen:
                seen.add(f.name)
                results.append(f.name)
    except OSError:
        pass
    return results


class Runner(Protocol):
    """How `_bash` runs a resolved command line: takes the context, the command
    line, and the working directory, and returns the process exit code."""

    def __call__(self, ctx: Context, cmdline: str, cwd: Path) -> int: ...


def _run_interactive(ctx: Context, cmdline: str, cwd: Path) -> int:
    """Run *cmdline* with the child inheriting the terminal directly.

    Used for interactive subshells (a bash/python REPL, a bare `claude`
    session) where the process needs the real TTY for its prompt and colours.
    Sacrifice: input/output is not captured in the session log.
    Returns the process exit code.
    """
    rc = subprocess.run(cmdline, shell=True, cwd=cwd, check=False).returncode
    if rc != 0:
        ctx.console.print(f'[error]exec error:[/error] {cmdline}')
    return rc


def _run_streamed(ctx: Context, cmdline: str, cwd: Path) -> int:
    """Run *cmdline*, streaming combined stdout/stderr through 'sys.stdout'.

    Routing the output through 'sys.stdout' (rather than inheriting the
    process file descriptors) lets the shell's session-log tee capture it,
    while the user still sees it live.  Returns the process exit code.
    """
    with subprocess.Popen(cmdline, shell=True, cwd=cwd, text=True, bufsize=1,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
        if proc.stdout is None:
            ctx.console.print(f'[error]no stdout[/error] {cmdline}')
            return 1
        for line in proc.stdout:
            sys.stdout.write(line)
        sys.stdout.flush()
        return proc.wait()


@command(requires=('shell:execute',), name='!',
         help_text='Run a bash command.',
         usage='\t! <command> [args]...\n'
               '\t! sh → escape to a bash shell.\n'
               '\t! py → escape to a python interpreter.\n',
         aliases=('sh', 'bash',),
         completer=_bash_completer)
def _bash(ctx: Context, *args: str) -> int:
    """Run a shell command from the shell, returning its exit code.

    Three forms escape into an *interactive* session that takes over the terminal:

        `! sh` / `! bash`       an interactive bash subshell, in the solution dir
        `! py` / `! python`     an interactive Python interpreter, in the repo root
        `! claude [prompt]`     Claude Code, in the repo root

    Any other command (`! ls`, `! git diff`, …) runs non-interactively in the
    current problem's solution directory — so paths are relative to that problem's
    files — with its output streamed through the shell (so `solver -s` can log it).
    After the command finishes, the problem specials are refreshed (↻) in case it
    changed the files.

    Aliased as `sh` and `bash`, so `sh <command>` is shorthand for `! <command>`.
    """
    if not (cmdline := ' '.join(shlex.quote(a) for a in args)):
        ctx.console.print('[muted]usage:[/muted] [accent]! <command ...>[/accent]')
        return ExitCodes.EXIT_USAGE
    # Pick a runner for the command.  Interactive subshells (sh/bash, py, claude) take over the terminal directly;
    # other command streams through sys.stdout so the shell's session-log tee can capture its output.
    runner: Runner
    if cmdline in ('sh', 'bash'):
        cmdline = '/usr/bin/bash'
        cwd: Path = ctx.variables.problem.solution_dir
        runner = _run_interactive
    elif cmdline in ('py', 'python'):
        cmdline = sys.executable
        cwd = config.root_dir
        runner = _run_interactive
    elif cmdline == 'claude' or cmdline.startswith('claude '):
        cwd = config.root_dir
        runner = _run_interactive
    else:
        cwd = ctx.variables.problem.solution_dir
        runner = _run_streamed

    try:
        rc: int = runner(ctx, cmdline, cwd)
    except OSError as exc:
        ctx.console.print(f'[error]exec error:[/error] {exc}')
        return ExitCodes.EXIT_ERROR
    if rc != 0:
        ctx.console.print(f'[muted]{ctx.raw_line.lstrip()}[/muted] '
                          f'[accent.dim]→[/accent.dim] '
                          f'[warning]{rc}[/warning]')
    return rc
