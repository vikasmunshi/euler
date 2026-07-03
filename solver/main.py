#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Entry point for the "solver shell" CLI."""
from __future__ import annotations

__all__ = ['main']

import argparse

from solver.config import config
from solver.shell import SolverShell
from solver.utils.loader import load_commands


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:  # pragma: no cover — manual entry
    """Parse CLI arguments and launch the solver shell.

    Arguments:
        (none)      Launch an interactive shell session.
        COMMANDS    Run as a single command block, then exit with its status.

    Returns:
        The exit status of the command block, or 0 on clean interactive exit.
    """
    parser = argparse.ArgumentParser(prog='solver', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('cmdline', nargs='*',
                        help='run a command block, then exit with its status; omit for an interactive shell')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {config.version}')
    parser.add_argument('-s', '--save', action='store_true', help=f'tee console output to {config.session_file.name}')

    args = parser.parse_args(argv)

    load_commands()
    shell = SolverShell(save=args.save and not args.cmdline)
    if args.cmdline:
        return shell.run_command(args.cmdline)
    return shell.run_interactive(intro_message='')


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
