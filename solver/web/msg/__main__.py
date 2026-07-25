#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Message service entry point: ``python -m solver.web.msg``.

Run by the root-owned ``euler-msg.service`` as the ``euler-msg`` user from the
``/opt/euler`` system venv, configured entirely by the environment (the unit's
``EnvironmentFile=/etc/euler/msg.env``). Binds the public and admin unix sockets,
sets their group/mode, and serves until SIGTERM.

The unit runs this ``RestrictAddressFamilies=AF_UNIX``: this process cannot open a
network socket at all, which is what dropping the mail path bought (web-server-guide
§ Messaging — *No mail*). Keep it that way — everything here speaks over
``/run/euler`` and ``/run/euler-adm``.

For local testing every path is overridable::

    EULER_MSG_STATE_DIR=/tmp/euler-msg EULER_MSG_SOCKET=/tmp/msg.sock \\
    EULER_MSG_ADMIN_SOCKET=/tmp/msg-admin.sock EULER_MSG_ADMIN_TOKEN=dev \\
    EULER_USER_SOCKET_DIR= python -m solver.web.msg
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import signal
from pathlib import Path

from aiohttp import web

from solver.web.msg.app import MessageService, build_admin_app, build_app
from solver.web.msg.config import MsgConfig

log = logging.getLogger('euler-msg')


async def _bind(app: web.Application, path: Path, group: str) -> web.AppRunner:
    """Serve *app* on the unix socket at *path*.

    With a *group*, the socket is ``0660`` + chgrp'd (the public socket: every
    collaborator uid connects via ``euler-web``). With an **empty** *group* it is
    ``0600`` — private to the service user; only root reaches it via sudo (the admin
    plane). Access logging is disabled: message subjects and thread ids have no
    business in the journal. No permission to chgrp (a dev run outside the deployed
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
    config = MsgConfig.from_env()
    config.state_dir.mkdir(parents=True, exist_ok=True)
    service = MessageService(config)
    runners = [
        await _bind(build_app(service), config.socket_path, config.socket_group),
        await _bind(build_admin_app(service), config.admin_socket_path, config.admin_socket_group),
    ]
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)
    log.info('msg service up (state: %s, staff: %d)',
             config.state_dir, len(service.policy.staff_boxes()))
    await stop.wait()
    log.info('shutting down')
    for runner in runners:
        await runner.cleanup()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
    asyncio.run(serve())


if __name__ == '__main__':
    main()
