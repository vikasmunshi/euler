#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Sign every web user out ahead of a shutdown: run **under sudo** by `logout-all` and `make logout-web`.

Each running per-user instance keeps its own countdown (:mod:`euler_webshell.user.logout`); this
starts them, waits for them all, then revokes every session and remember-me token, which is what
signs out a user with no tab open. Only instances already running are called: dialling a socket
is what starts a stopped one. `--extend` adds time and returns, leaving the run that is waiting
to finish the job; `--now` closes every shell at once, notice or no notice, and finishes it here.

Invocation::

    sudo <venv-python> -m euler_webshell.logout_all [reason] [--seconds N] [--limit N]
    sudo <venv-python> -m euler_webshell.logout_all --extend N
    sudo <venv-python> -m euler_webshell.logout_all --now
"""
from __future__ import annotations

__all__ = ['DEFAULT_LIMIT', 'DEFAULT_REASON', 'DEFAULT_SECONDS', 'main']

import argparse
import http.client
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from euler_site.auth.admin import revoke_all
from euler_site.auth.client import request
from solver.config.env import load_spec

DEFAULT_REASON: str = 'the server is shutting down'
#: The countdown, and how long running work may hold the shell past it in all.
DEFAULT_SECONDS: int = 60
DEFAULT_LIMIT: int = 600

_ROUTE: str = '/internal/logout-notice'
_POLL_SECONDS: float = 2.0


def running_instances() -> list[str]:
    """The slugs of the per-user instances running now."""
    listed = subprocess.run(['systemctl', 'list-units', 'euler-user@*.service', '--state=active',
                             '--plain', '--no-legend'], capture_output=True, text=True, check=False)
    units = [line.split()[0] for line in listed.stdout.splitlines() if line.strip()]
    return [unit.removeprefix('euler-user@').removesuffix('.service') for unit in units]


def _call(slug: str, method: str, body: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """One call to *slug*'s notice route; None if the instance is gone or predates the route."""
    socket_path = Path(load_spec('auth').raw('user_socket_dir')) / f'user-{slug}.sock'
    try:
        status, data = request(str(socket_path), method, _ROUTE, body=body, timeout=5.0)
    except (OSError, http.client.HTTPException):
        return None
    return data if status == 200 and isinstance(data, dict) else None


def _push(slugs: list[str], body: dict[str, Any]) -> list[str]:
    """Send *body* to every instance; return the ones that took it, naming the rest."""
    reached = [slug for slug in slugs if _call(slug, 'POST', body) is not None]
    for slug in sorted(set(slugs) - set(reached)):
        print(f'note: {slug} did not answer; its shell closes when the instance stops')
    return reached


def _wait(slugs: list[str]) -> None:
    """Block until no instance has a notice standing, reporting who is still holding it up."""
    waiting = list(slugs)
    shown: list[str] = []
    while waiting:
        states = {slug: _call(slug, 'GET') for slug in waiting}
        waiting = [slug for slug, state in states.items() if state is not None and state.get('active')]
        held = [slug for slug in waiting if (states[slug] or {}).get('running')]
        if held != shown:
            print(f'waiting on running work: {", ".join(held)}' if held else 'no running work left')
            shown = held
        if waiting:
            time.sleep(_POLL_SECONDS)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog='logout_all', description=__doc__.splitlines()[0] if __doc__ else '')
    parser.add_argument('reason', nargs='?', default=DEFAULT_REASON)
    parser.add_argument('--seconds', type=int, default=DEFAULT_SECONDS)
    parser.add_argument('--limit', type=int, default=DEFAULT_LIMIT)
    parser.add_argument('--extend', type=int, default=0)
    parser.add_argument('--now', action='store_true')
    args = parser.parse_args(argv)

    slugs = running_instances()
    if args.extend:
        print(f'added {args.extend}s on {len(_push(slugs, {"extend": args.extend}))} instance(s)')
        return 0
    body = {'now': True} if args.now else {'reason': args.reason, 'seconds': args.seconds, 'limit': args.limit}
    reached = _push(slugs, body)
    print(f'closing the shells on {len(reached)} instance(s)' if args.now
          else f'notice on {len(reached)} instance(s): {args.reason}')
    try:
        _wait(reached)
    except KeyboardInterrupt:
        print('stopped waiting: the countdowns go on, but nobody is signed out until `--now` runs',
              file=sys.stderr)
        return 130
    try:
        print(f'revoked {revoke_all()} session(s) and remember-me token(s)')
    except (OSError, RuntimeError) as exc:
        print(f'error: could not revoke the sessions ({exc})', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
