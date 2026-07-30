#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Minimal HTTP-over-unix-socket client, shared by the service tiers (stdlib only).

Used by the callers that must not depend on aiohttp — the shell commands and the
identity resolver, which run inside the solver process:

- the `users` shell command (:mod:`solver.web.auth.commands`) → the auth admin socket;
- shell-ticket redemption (:mod:`solver.auth.identity`) → the auth public socket;
- the `msg` shell command (:mod:`solver.web.msg.commands`) → the message spool.

Deliberately tiny: JSON in/out, one request per connection, no retries — every
socket is local and the service answers immediately or not at all.

This lives at :mod:`solver.web` rather than under one service package so a second
service can use it without importing the first: :mod:`solver.web.msg` must not pull
:mod:`solver.web.auth` into its process (web-server-guide § Messaging).
"""
from __future__ import annotations

__all__ = ['request']

import http.client
import json
import socket
from typing import Any


class _UnixConnection(http.client.HTTPConnection):
    """An HTTPConnection whose transport is a unix domain socket."""

    def __init__(self, socket_path: str, timeout: float) -> None:
        super().__init__('localhost', timeout=timeout)
        self._socket_path = socket_path

    def connect(self) -> None:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.settimeout(self.timeout)
            sock.connect(self._socket_path)
        except BaseException:
            # A failed connect never reaches `self.sock`, so the caller's `close()` in
            # `request()` cannot reach this socket either — without closing it here the fd
            # leaks. That is the *expected* path for two callers, not a rare one: the `msg`
            # command probes the public socket on every invocation from the operator's
            # terminal (which is deliberately not in euler-web), and `notify_staff` runs on
            # every checkout with no spool deployed.
            sock.close()
            raise
        self.sock = sock


def request(socket_path: str, method: str, path: str, *,
            body: dict[str, Any] | None = None,
            headers: dict[str, str] | None = None,
            timeout: float = 10.0) -> tuple[int, dict[str, Any] | str]:
    """One HTTP request over the unix socket; return `(status, parsed body)`.

    The body comes back as a dict when the response is JSON, else as text.
    Raises OSError if the socket is absent/refusing (service not running or the
    caller lacks group access).
    """
    connection = _UnixConnection(socket_path, timeout)
    try:
        payload = json.dumps(body).encode() if body is not None else None
        all_headers = {'Content-Type': 'application/json', **(headers or {})}
        connection.request(method, path, body=payload, headers=all_headers)
        response = connection.getresponse()
        raw = response.read().decode('utf-8', 'replace')
        try:
            parsed: dict[str, Any] | str = json.loads(raw)
            if not isinstance(parsed, dict):
                parsed = raw
        except json.JSONDecodeError:
            parsed = raw
        return response.status, parsed
    finally:
        connection.close()
