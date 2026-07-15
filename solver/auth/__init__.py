#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The authorization kernel — identity, profiles, and permissions (DD-12).

One RBAC engine shared by the shell and the web: it resolves a
:class:`~solver.auth.subject.Subject` from the identity planes (DD-9/DD-12) and
answers permission queries against ``authorizations.json`` (the deployed
``/etc/euler`` system of record, DD-12). The command decorator and the web app
router are the two enforcement points; both check the one subject.

This kernel supersedes the shell-only ``commands.csv`` and the web-only
profile-on-user-record — the two policies that did not compose across channels.

Import discipline: stdlib-only and **no ``solver.config`` dependency** — config
imports the resolver during its own construction. The web *authentication*
service (``solver.web.auth``: SRP, sessions, tickets) is a separate package that
*imports* this kernel to turn an authenticated email into a subject.
"""
from __future__ import annotations

__all__ = ['Subject', 'Authorizations', 'resolve_subject', 'slugify', 'LADDER',
           'FAILCLOSED_PROFILE', 'AUTHZ_FILE_ENV', 'DEFAULT_AUTHZ_FILE', 'TICKET_ENV']

from solver.auth.authorizations import (AUTHZ_FILE_ENV, DEFAULT_AUTHZ_FILE,
                                        FAILCLOSED_PROFILE, Authorizations)
from solver.auth.identity import TICKET_ENV, resolve_subject, slugify
from solver.auth.subject import LADDER, Subject
