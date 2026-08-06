#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The message admin plane CLI: run **under sudo** by the `msg` shell command.

The spool's public socket is `0660 euler-msg:euler-web`, and the operator's own uid is
deliberately **not** in `euler-web` — that group is for the service tier, and putting
the host's most exposed uid in it would hand every browser and dev tool on the box a
connection to the app plane. So the operator reaches the spool the same way they reach
the auth service: as root, via `sudo`, over the `0600` admin socket, with the token
that lives only in root-readable `/etc/euler/msg.env`.

This is a **thin authenticated proxy**, not a second command surface: it takes a method
and an admin path, injects the invoking identity, and prints the service's reply as one
JSON line. One renderer (in :mod:`solver.web.msg.commands`) then serves both channels,
so the terminal and the web shell cannot drift in what they show.

Two details are deliberate:

- **The body arrives on stdin**, never in `argv`. A message body in the process table
  would be readable by every uid on the host via `/proc`, which is precisely the
  exposure the spool exists to avoid.
- **The identity is the invoking user** (`SUDO_USER`), not an argument. Root could
  assert anything here — the point is that a typo cannot file a message under a
  stranger's name, and the profile check still runs against `authorizations.json`.

Invocation (see :mod:`solver.web.msg.commands` for the shell wrapper)::

    echo '{"body": "…"}' | sudo <venv-python> -m solver.web.msg.admin api POST /admin/…
"""
from __future__ import annotations

__all__ = ['main']

import getpass
import json
import os
import sys
from pathlib import Path
from typing import Any

from solver.web.envfile import env_file_values
from solver.config.env import load_spec
from solver.web.unixhttp import request

_METHODS = ('GET', 'POST', 'DELETE')


def _fail(message: str, code: int = 1) -> int:
    print(f'error: {message}', file=sys.stderr)
    return code


def _invoking_identity() -> str:
    """The operator behind the sudo: `SUDO_USER`, else this process's own login."""
    who = os.environ.get('SUDO_USER', '').strip()
    if who:
        return who
    try:
        return getpass.getuser()
    except OSError:
        return ''


def _api(method: str, path: str, body: dict[str, Any]) -> tuple[int, dict[str, Any] | str]:
    """One call to the euler-msg admin socket, with the token from the scoped env file."""
    env_file = env_file_values(Path(os.environ.get('EULER_MSG_ENV', '/etc/euler/msg.env')))
    token = os.environ.get('EULER_MSG_ADMIN_TOKEN') or env_file.get('EULER_MSG_ADMIN_TOKEN', '')
    admin_socket = load_spec('msg').entries['admin_socket_path']
    socket_path = (os.environ.get(admin_socket.env_var) or env_file.get(admin_socket.env_var)
                   or admin_socket.default)
    if not token:
        raise RuntimeError('EULER_MSG_ADMIN_TOKEN not found '
                           '(is /etc/euler/msg.env deployed, and are you root?)')
    return request(socket_path, method, path, body=body or None,
                   headers={'X-Admin-Token': token}, timeout=15.0)


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[0] != 'api' or argv[1] not in _METHODS:
        print(f'usage: python -m solver.web.msg.admin api {{{"|".join(_METHODS)}}} <admin-path>  '
              '(JSON body on stdin)', file=sys.stderr)
        return 2
    method, path = argv[1], argv[2]
    if not path.startswith('/admin/'):
        return _fail('only /admin/* paths are reachable from this CLI')

    raw = sys.stdin.read().strip() if not sys.stdin.isatty() else ''
    try:
        body: Any = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return _fail('malformed JSON body on stdin')
    if not isinstance(body, dict):
        return _fail('the body must be a JSON object')

    identity = _invoking_identity()
    if not identity:
        return _fail('could not determine the invoking identity')
    body['identity'] = identity
    # Also on the query string: the service reads the body first and falls back to the
    # query, and a GET carrying a body is the odd shape of the two.
    joiner = '&' if '?' in path else '?'
    path = f'{path}{joiner}identity={identity}'

    try:
        status, data = _api(method, path, body)
    except TimeoutError:
        return _fail('timed out waiting for the message service')
    except (OSError, RuntimeError) as exc:
        return _fail(f'message admin plane error ({exc}) — '
                     'is euler-msg.service running, and are you root?')
    print(json.dumps({'status': status, 'body': data}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
