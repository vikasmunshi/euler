#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Web authentication for solver-web.

SRP-6a credential verification and the user (verifier) store, kept wholly
separate from ``solver.crypto`` (solution encryption): this package gates web
access and shares no key material with the encryption master key.
"""
from __future__ import annotations

__all__ = ['SrpClient', 'SrpServer', 'SrpToken', 'make_srp_token', 'compute_verifier',
           'verify_password', 'VERSION', 'UserRecord', 'UserStore', 'normalize_email']

from solver.web.auth.srp import (VERSION, SrpClient, SrpServer, SrpToken, compute_verifier,
                                 make_srp_token, verify_password)
from solver.web.auth.users import UserRecord, UserStore, normalize_email
