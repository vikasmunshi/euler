#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Per-user service entry point: ``python -m solver.web.user`` (DD-5/MT-4).

Run by ``euler-user@<slug>.service`` as that collaborator's own
``euler-user-<slug>`` uid from the ``/opt/euler`` system venv, configured entirely by
the environment (``EULER_USER_SLUG``, ``EULER_REPO_ROOT`` → their ``~/euler`` clone).

Three ways to get a listener, in order:

1. **systemd socket activation** — the ``euler-user@<slug>.socket`` unit creates
   ``/run/euler/user-<slug>.sock`` and passes it as ``fd 3`` (``LISTEN_FDS``); the
   service is spawned on the first Caddy connection and reuses that socket.
2. **dev TCP** — ``EULER_USER_TCP=127.0.0.1:8084`` (the harness path).
3. **plain unix bind** — ``EULER_USER_SOCKET`` (an always-on run without a .socket unit).

Serves until SIGTERM; cleanup reaps every PTY child (DD-14)::

    EULER_USER_TCP=127.0.0.1:8084 EULER_USER_SLUG=me-abc123 \\
    EULER_AUTH_SOCKET=/tmp/dev-auth.sock python -m solver.web.user
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import signal
import socket

from aiohttp import web

from solver.web.user.app import build_app
from solver.web.user.config import UserConfig

log = logging.getLogger('euler-user')

#: The first file descriptor systemd passes for socket activation (sd_listen_fds).
_SD_LISTEN_FDS_START = 3


def _systemd_socket() -> socket.socket | None:
    """The listener systemd passed for socket activation, or None (not activated)."""
    if int(os.environ.get('LISTEN_FDS', '0') or '0') < 1:
        return None
    if int(os.environ.get('LISTEN_PID', '0') or '0') != os.getpid():
        return None                      # the fds were meant for a different process
    return socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, fileno=_SD_LISTEN_FDS_START)


async def serve() -> None:
    config = UserConfig.from_env()
    runner = web.AppRunner(build_app(config), access_log=None)
    await runner.setup()

    activated = _systemd_socket()
    if activated is not None:                             # prod: socket-activated
        site: web.BaseSite = web.SockSite(runner, activated)
        await site.start()
        log.info('listening on the systemd socket (user %s)', config.slug or '<unpinned>')
    elif config.tcp_bind:                                 # dev: TCP listener
        host, _, port = config.tcp_bind.partition(':')
        site = web.TCPSite(runner, host or '127.0.0.1', int(port or '8084'))
        await site.start()
        log.info('listening on %s (tcp, dev)', config.tcp_bind)
    else:                                                 # always-on unix bind
        path = config.socket_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.unlink(missing_ok=True)
        site = web.UnixSite(runner, str(path))
        await site.start()
        os.chmod(path, 0o660)
        try:
            shutil.chown(path, group=config.socket_group)
        except (LookupError, PermissionError, OSError) as exc:
            log.warning('could not set group %r on %s (%s) — dev run?', config.socket_group, path, exc)
        log.info('listening on %s (group %s)', path, config.socket_group)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)
    log.info('per-user service up (user %s)', config.slug or '<unpinned dev>')
    await stop.wait()
    log.info('shutting down')
    await runner.cleanup()               # on_cleanup reaps every shell (DD-14)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
    asyncio.run(serve())


if __name__ == '__main__':
    main()
