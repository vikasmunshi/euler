#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Entry point for the "solver shell" CLI."""
from __future__ import annotations

import argparse
import importlib
import sys
from typing import Optional

from solver.core.config import config
from solver.core.lock import acquire_workspace_lock
from solver.core.shell import SolverShell


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv: Optional[list[str]] = None) -> int:  # pragma: no cover — manual entry
    """Parse CLI arguments and launch the solver shell.

    Arguments:
        (none)      Launch an interactive shell session.
        COMMANDS    Semicolon-separated commands to queue at startup; exits when done
                    unless "-c" is also given.

    Flags:
        -c / --continue     Stay interactive after the queued commands finish.

    Returns:
        0 on clean exit.
    """
    parser = argparse.ArgumentParser(prog='solver', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1.0')
    parser.add_argument('-c', '--continue', action='store_true', help='stay interactive after running cmdline')
    parser.add_argument('cmdline', nargs='*', help='run cmdline; quote and semicolon-separate multiple commands')
    args = parser.parse_args(argv)
    startup: list[str] = []

    # positional cmdline: split on ';' exit after unless -c
    if args.cmdline:
        startup.extend(c.strip() for c in ' '.join(args.cmdline).split(';') if c.strip())
        if not getattr(args, 'continue'):
            startup.append('exit')
    #: Modules imported for their side-effects (command registrations) before the shell starts.
    for module in config.modules_with_commands:
        importlib.import_module(module)
    with acquire_workspace_lock():
        return SolverShell().run(intro=not bool(startup), commands=startup)


__all__ = ('main',)
if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
