#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Entry point for the "solver" CLI.

Parses command-line arguments and launches: class:`solver.cli.SolverShell`.

Usage:

    solver                          # interactive shell
    solver "cmd1; cmd2"             # run commands, then exit
    solver -c "cmd1; cmd2"          # run commands, stay interactive
    solver --no-capture "cmd1"      # run without session capture
"""
from __future__ import annotations

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from solver.cli import SolverShell
from solver.session import SessionCapture


def main() -> int:
    """Parse CLI arguments and launch the solver shell.

    Arguments:
        (none)      Launch an interactive shell session.
        COMMANDS    Semicolon-separated commands to queue at startup; exits when done
                    unless "-c" is also given.

    Flags:
        -c / --continue     Stay interactive after the queued commands finish.
        --capture           Tee all output to a timestamped session log (default).
        --no-capture        Disable session capture.

    Returns:
        0 on clean exit.
    """
    parser = ArgumentParser(prog='solver', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1.0')
    parser.add_argument('-c', '--continue', action='store_true', help='stay interactive after running cmdline commands')
    parser.add_argument('-s', '--save-session', action='store_true', default=False, help='save session to a log-file')
    parser.add_argument('cmdline', nargs='?', metavar='COMMANDS',
                        help='optional commands to run at startup (semicolon-separated)')
    args = parser.parse_args()
    startup: list[str] = []

    # positional cmdline: split on ';' and queue; exit after unless -c
    if args.cmdline:
        startup.extend(c.strip() for c in args.cmdline.split(';') if c.strip())
        if not getattr(args, 'continue'):
            startup.append('exit')

    if args.save_session:
        with SessionCapture() as session:
            return session.shell.execute(commands=startup or None)
    return SolverShell().execute(commands=startup or None)


if __name__ == '__main__':
    raise SystemExit(main())
