#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Entry point for the "solver shell" CLI."""
from __future__ import annotations

__all__ = ['main']

import argparse

from solver.config import config, enter_repo
from solver.shell import SolverShell
from solver.shell.extension import Extension, ExtensionError, load_extension
from solver.shell.login import identify, status_line, unlock
from solver.utils.loader import load_commands


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None, *, extension: Extension | None = None) -> int:  # pragma: no cover
    """Parse CLI arguments and launch the solver shell.

    Arguments:
        (none)      Launch an interactive shell session.
        COMMANDS    Run as a single command block, then exit with its status.

    *extension* is how a package built on the shell adds commands and overlays to it
    (:mod:`solver.shell.extension`); the plain `solver` entry point passes none.

    Returns:
        The exit status of the command block, or 0 on clean interactive exit.
    """
    # The shell runs *from* the tree it found, with a PATH that can see the venv — and it
    # says so, here, rather than inheriting it as a side effect of importing configuration.
    # Everything downstream assumes it: `config.scripts` are repo-relative (`./scripts/…`),
    # `!` runs bash in the working tree, and `claude-solve` launches Claude at the root.
    enter_repo(config.root_dir)

    parser = argparse.ArgumentParser(prog='solver', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('cmdline', nargs='*',
                        help='run a command block, then exit with its status; omit for an interactive shell')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {config.version}')
    parser.add_argument('-s', '--save', action='store_true', help=f'tee console output to {config.session_file.name}')

    args = parser.parse_args(argv)

    # Who this is, before any command loads: every command's floor is checked against the
    # subject as it registers. Not a CLI flag — no caller picks its command set by argument.
    identify(extension)
    load_commands()
    if extension is not None:
        try:
            load_extension(extension)
        except ExtensionError as exc:
            raise SystemExit(f'extension: {exc} — refusing to start') from None
    unlock(extension)
    shell = SolverShell(save=args.save and not args.cmdline)
    if args.cmdline:
        return shell.run_command(args.cmdline)
    return shell.run_interactive(intro_message='', status=status_line,
                                 on_start=extension.on_start if extension is not None else None)


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
