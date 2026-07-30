#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""HTTP-over-unix-socket client for the auth service — re-export of the shared one.

The implementation moved to :mod:`solver.web.unixhttp` when the message spool
(:mod:`solver.web.msg`) needed the same client: a second service must be able to
talk over a unix socket without importing this package, since loading auth's
modules into another service's process would recouple the two and defeat the
isolation that gave the spool its own uid (web-server-guide § Messaging).

This module stays as the auth tier's name for it, so its callers — the `users`
command and the identity resolver — need no edit.
"""
from __future__ import annotations

__all__ = ['request']

from solver.web.unixhttp import request
