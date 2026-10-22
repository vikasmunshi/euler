#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The per-user web service: one collaborator's content **and** web shell.

Replaces the per-*profile* content (:mod:`euler_site.site`) and web-shell
(:mod:`euler_webshell.ws`) instances with a single per-*user* service: one process per
collaborator, born as their own uid (named for their `system_slug`), reading their own clone
and vault, serving both the content routes and `/ws` on one socket that Caddy
dials by `X-User-Slug`. The old per-profile services stay as the
libraries this composes — the content handlers (:mod:`euler_site.site.app`) and the
PTY machinery (:mod:`euler_webshell.ws`).
"""
