#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The web-shell service: the solver PTY terminal over WebSocket.

One aiohttp app per profile instance (``euler-ws@<profile>``, uid
``euler-ws-<profile>``, socket ``/run/euler/ws-<profile>.sock``), behind Caddy's
``forward_auth`` + per-profile routing. ``GET /ws`` attaches the browser terminal
to the signed-in user's **persistent** solver shell:

- identity arrives as the trusted ``X-User``/``X-Profile`` headers; the
  instance refuses a profile that differs from its ``EULER_PROFILE`` pin;
- attach is gated on the reader floor (the "may run the solver at all"
  grant) via the :mod:`solver.auth` kernel;
- on first attach the service forwards the caller's session cookie to the auth
  service's ``POST /shell-ticket`` and forks ``python -m solver`` with only
  ``SOLVER_TICKET`` (+ ``TERM``) added to the child environment — the child
  redeems the ticket and becomes the web-channel Subject;
- the shell survives disconnects: a background drainer buffers output
  for replay, reconnects redraw, extra tabs share the one shell; teardown is
  in-shell ``exit``, the auth service's ``POST /internal/logout`` push
  (logout/revocation), or service stop.

Wire protocol: **binary frames are raw PTY bytes both ways**; a text frame
``{"resize": [cols, rows]}`` propagates the browser terminal's geometry.
"""
from __future__ import annotations

__all__: list[str] = []
