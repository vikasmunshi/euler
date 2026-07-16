#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Entry point for the "solver shell" CLI."""
from __future__ import annotations

__all__ = ['main']

import argparse

from solver.config import config
from solver.crypto.keys import unlock_session
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

    # The channel (terminal / web) is **not** a CLI flag: it comes from the
    # resolved subject — the checkout-owner uid or a redeemed shell ticket — so no
    # caller can choose the command set it gets by passing an argument.
    load_commands()

    # The vault gate, before any command runs. `id` and `env` rest encrypted, and the
    # readers that need them — the git clean/smudge filter above all — are
    # subprocesses with no terminal to be asked anything: the key must reach them as
    # the inherited key file this call materialises. So the asking happens here, once,
    # at the one moment there is still a person to ask.
    # It is a no-op when there is no vault and when $EULER_VAULT_PASSWORD answers. A
    # declined or wrong password is not fatal — the shell runs locked, and the private
    # solutions and `claude-api` are what stay unavailable.
    #
    # Only the TERMINAL is ever asked. On the web the vault is the browser's job: it
    # derives PK from the password it already holds and the service writes the key file
    # before forking this shell (§ the web unlock path). A web shell that stopped to ask
    # for a vault password would be asking for something the design deliberately never
    # routes through the server — and, on a locked vault, would stall every attach behind
    # a prompt. `vault unlock` still prompts on any channel: that one the user asked for.
    unlock_session(interactive=config.subject.channel == 'terminal')
    shell = SolverShell(save=args.save and not args.cmdline)
    if args.cmdline:
        return shell.run_command(args.cmdline)
    return shell.run_interactive(intro_message='')


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
