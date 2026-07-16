#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Auth service entry point: ``python -m solver.web.auth``.

Run by the root-owned ``euler-auth.service`` as the ``euler-auth`` user from
the ``/opt/euler`` system venv, configured entirely by the environment (the
unit's ``EnvironmentFile=/etc/euler/auth.env``). Binds the public and admin
unix sockets, sets their group/mode, and serves until SIGTERM.

For local testing every path is overridable::

    EULER_AUTH_STATE_DIR=/tmp/euler-auth EULER_AUTH_SOCKET=/tmp/auth.sock \\
    EULER_AUTH_ADMIN_SOCKET=/tmp/auth-admin.sock EULER_ADMIN_TOKEN=dev \\
    EULER_BASE_URL=https://localhost python -m solver.web.auth
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import signal
from pathlib import Path

from aiohttp import web

from solver.web.auth.app import AuthService, build_admin_app, build_public_app
from solver.web.auth.config import AuthConfig

log = logging.getLogger('euler-auth')


async def _bind(app: web.Application, path: Path, group: str) -> web.AppRunner:
    """Serve *app* on the unix socket at *path*.

    With a *group*, the socket is ``0660`` + chgrp'd (the public socket: Caddy
    and the app tier connect via ``euler-web``). With an **empty** *group* it is
    ``0600`` — private to the service user; only root reaches it via sudo (the
    admin plane). Access logging is disabled (tokens travel in query
    strings). No permission to chgrp (a dev run outside the deployed
    identities) is logged and tolerated.
    """
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    site = web.UnixSite(runner, str(path))
    await site.start()
    if group:
        os.chmod(path, 0o660)
        try:
            shutil.chown(path, group=group)
        except (LookupError, PermissionError, OSError) as exc:
            log.warning('could not set group %r on %s (%s) — dev run?', group, path, exc)
        log.info('listening on %s (group %s)', path, group)
    else:
        os.chmod(path, 0o600)
        log.info('listening on %s (private)', path)
    return runner


async def serve() -> None:
    config = AuthConfig.from_env()
    config.state_dir.mkdir(parents=True, exist_ok=True)
    service = AuthService(config)
    runners = [
        await _bind(build_public_app(service), config.socket_path, config.socket_group),
        await _bind(build_admin_app(service), config.admin_socket_path, config.admin_socket_group),
    ]
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)
    log.info('auth service up (state: %s, base: %s)', config.state_dir, config.base_url)
    await stop.wait()
    log.info('shutting down')
    for runner in runners:
        await runner.cleanup()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
    asyncio.run(serve())


if __name__ == '__main__':
    main()
