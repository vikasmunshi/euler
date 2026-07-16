#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Content service entry point: ``python -m solver.web.site``.

Run by ``euler-content@<profile>.service`` as the per-profile ``euler-content``
uid from the ``/opt/euler`` system venv, configured entirely by the environment.
Binds the public unix socket (``/run/euler/content.sock``, group ``euler-web`` —
Caddy's upstream) and serves until SIGTERM.

For local testing, bind a TCP port and serve the static assets from the app::

    EULER_CONTENT_TCP=127.0.0.1:8081 EULER_CONTENT_SERVE_STATIC=1 \\
    python -m solver.web.site
    # then: curl -H 'X-User: me' -H 'X-Profile: admin' http://127.0.0.1:8081/
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import signal

from aiohttp import web

from solver.web.site.app import build_app
from solver.web.site.config import SiteConfig

log = logging.getLogger('euler-content')


async def serve() -> None:
    config = SiteConfig.from_env()
    runner = web.AppRunner(build_app(config), access_log=None)
    await runner.setup()

    if config.tcp_bind:                                   # dev: TCP listener
        host, _, port = config.tcp_bind.partition(':')
        site: web.BaseSite = web.TCPSite(runner, host or '127.0.0.1', int(port or '8081'))
        await site.start()
        log.info('listening on %s (tcp, dev)', config.tcp_bind)
    else:                                                 # prod: unix socket
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
    log.info('content service up (repo: %s)', config.repo_root)
    await stop.wait()
    log.info('shutting down')
    await runner.cleanup()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
    asyncio.run(serve())


if __name__ == '__main__':
    main()
