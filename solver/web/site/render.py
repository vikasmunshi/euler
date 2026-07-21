#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The full-page-vs-block render contract (§4.5).

A content route renders either the **whole page** or a **named block** of the
*same* template, so a full navigation and an htmx fragment-swap share one source
of truth. The block path uses Jinja's own API — ``tmpl.blocks[name](ctx)`` — in
a small helper rather than pulling in ``jinja2-fragments`` (a pinned dep that is
mostly Flask/Quart glue for these few lines).

:func:`render` is the one entry point handlers call: when the request is an htmx
fetch (``HX-Request: true``) *and* a ``block`` is named, it returns just that
block; otherwise the full template. Either way the shared context (the request's
CSP nonce and resolved subject) is injected, and the response is ``text/html``
so the shared CSP middleware stamps its header.

**Page chrome (web-server-guide § The site).** Breadcrumbs, the Actions menu and the
git chip live in the fixed header, which htmx never re-renders — so every *block*
response appends the ``_crumbs.html`` / ``_actions.html`` / ``_git.html`` partials
with ``hx-swap-oob``, keeping the header in step with the pane. A full-page render
places the same partials in the header directly (``oob`` unset).
"""
from __future__ import annotations

__all__ = ['render', 'render_block', 'is_htmx', 'SUBJECT_KEY', 'GIT_KEY']

from typing import Any

import aiohttp_jinja2
import jinja2
from aiohttp import web

from solver.web.csp import NONCE_KEY

#: aiohttp request key under which the identity middleware stores the Subject.
SUBJECT_KEY: str = 'subject'
#: aiohttp request key under which the git middleware stores this clone's GitState
#: (:mod:`solver.web.site.gitstate`) — None where there is no readable clone.
GIT_KEY: str = 'git'
#: htmx sets this on every fetch; its presence selects fragment rendering.
_HX_HEADER = 'HX-Request'


def is_htmx(request: web.Request) -> bool:
    """True when *request* is an htmx-driven fetch (``HX-Request: true``)."""
    return request.headers.get(_HX_HEADER, '').lower() == 'true'


def _context(request: web.Request, extra: dict[str, Any] | None) -> dict[str, Any]:
    """The template context: the shared nonce + subject, then the handler's vars.

    ``crumbs`` / ``actions`` / ``git`` (the §6 page chrome) default empty so every
    template — and the chrome partials — can rely on them existing. ``git`` defaults
    to None, which is the chip's own inert state: the auth tier builds its own
    contexts and has no clone behind it, and neither does a signed-out visitor.
    """
    ctx: dict[str, Any] = {
        'csp_nonce': request.get(NONCE_KEY, ''),
        'subject': request.get(SUBJECT_KEY),
        'crumbs': [],
        'actions': [],
        'git': request.get(GIT_KEY),
    }
    if extra:
        ctx.update(extra)
    return ctx


def render_block(env: jinja2.Environment, template_name: str, block_name: str,
                 context: dict[str, Any]) -> str:
    """Render a single named ``{% block %}`` of *template_name* to a string.

    Only the block's own code runs — the template root does not. So anything a
    block needs must live *inside* it: a ``{% macro %}`` (or ``{% set %}``) at
    template top level exists on the full-page path and is undefined here.

    Raises :class:`KeyError` if the template has no block called *block_name* —
    a programming error (route/template mismatch), surfaced loudly.
    """
    tmpl = env.get_template(template_name)
    if block_name not in tmpl.blocks:
        raise KeyError(f'template {template_name!r} has no block {block_name!r}')
    ctx = tmpl.new_context(context)
    return ''.join(tmpl.blocks[block_name](ctx))


def render(request: web.Request, template_name: str,
           context: dict[str, Any] | None = None, *,
           block: str | None = None, status: int = 200,
           fragment: bool = False) -> web.Response:
    """Render *template_name* — its *block* for an htmx fetch, else the full page.

    *fragment* forces the block regardless of ``HX-Request``: the write routes
    always answer with a fragment (web-server-guide § The site), never the whole shell.
    """
    env = aiohttp_jinja2.get_env(request.app)
    ctx = _context(request, context)
    if block and (fragment or is_htmx(request)):
        # The pane fragment + the header chrome as out-of-band swaps (§6).
        oob_ctx = {**ctx, 'oob': True}
        body = (render_block(env, template_name, block, ctx)
                + env.get_template('_crumbs.html').render(oob_ctx)
                + env.get_template('_actions.html').render(oob_ctx)
                + env.get_template('_git.html').render(oob_ctx))
    else:
        body = env.get_template(template_name).render(ctx)
    return web.Response(text=body, content_type='text/html', status=status)
