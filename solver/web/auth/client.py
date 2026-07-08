#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Minimal HTTP-over-unix-socket client for the auth service (stdlib only).

Used by the two *callers* of the service that must not depend on aiohttp:

- the ``users`` shell command (:mod:`solver.web.auth.commands`), talking to the
  admin socket (DD-6);
- shell-ticket redemption in :mod:`solver.utils.identity` (DD-9), talking to
  the public socket.

Deliberately tiny: JSON in/out, one request per connection, no retries — both
sockets are local and the service answers immediately or not at all.
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
        sock.settimeout(self.timeout)
        sock.connect(self._socket_path)
        self.sock = sock


def request(socket_path: str, method: str, path: str, *,
            body: dict[str, Any] | None = None,
            headers: dict[str, str] | None = None,
            timeout: float = 10.0) -> tuple[int, dict[str, Any] | str]:
    """One HTTP request over the unix socket; return ``(status, parsed body)``.

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
