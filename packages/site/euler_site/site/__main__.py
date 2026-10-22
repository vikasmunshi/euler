#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Content service entry point: `python -m euler_site.site`.

Deployed as the **public site**: `euler-site.service` runs it as the `euler-site` uid from
the `/opt/euler` system venv with `EULER_SITE_PUBLIC=1`, serving the packaged content
(`euler-content`) on `/run/euler/site.sock` (group `euler-web` — Caddy's upstream) to
visitors who are not signed in. Without that flag it is the header-identity content app,
kept for local testing (signed-in pages are the per-user service's, `euler_webshell.user`).

For local testing, bind a TCP port and serve the static assets from the app::

    EULER_CONTENT_TCP=127.0.0.1:8081 EULER_CONTENT_SERVE_STATIC=1 \\
    python -m euler_site.site
    # then: curl -H 'X-User: me' -H 'X-Profile: admin' http://127.0.0.1:8081/
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import signal

from aiohttp import web

from euler_site.site.app import build_app, build_public_app
from euler_site.site.config import SiteConfig

log = logging.getLogger('euler-content')


async def serve() -> None:
    config = SiteConfig.from_env()
    runner = web.AppRunner(build_public_app(config) if config.public else build_app(config), access_log=None)
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
