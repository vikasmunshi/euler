#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The Cache-Control middleware (solver.web.cache): the two response classes, error
responses, and the hands-off cases.

What is being protected is the *absence* of a header: a response with no
``Cache-Control`` is heuristically cacheable, which is the stale-until-hard-refresh
bug. So every assertion here is "something was said", not merely "nothing broke".
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from solver.web.cache import NO_STORE, REVALIDATE, cache_middleware, directive_for
from tests import silence

silence()


class DirectiveTests(unittest.TestCase):
    def test_a_file_response_revalidates_everything_else_is_never_stored(self) -> None:
        self.assertEqual(directive_for(web.FileResponse(Path(__file__))), REVALIDATE)
        self.assertEqual(directive_for(web.Response(text='hi')), NO_STORE)
        self.assertEqual(directive_for(web.json_response({'a': 1})), NO_STORE)
        self.assertEqual(directive_for(web.HTTPNotFound()), NO_STORE)


class CacheMiddlewareTests(AioHTTPTestCase):
    async def get_application(self) -> web.Application:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.asset = Path(tmp.name) / 'thing.css'
        self.asset.write_text('body{}\n')

        async def page(_request: web.Request) -> web.StreamResponse:
            return web.Response(text='<p>hi</p>', content_type='text/html')

        async def api(_request: web.Request) -> web.StreamResponse:
            return web.json_response({'ok': True})

        async def file(_request: web.Request) -> web.StreamResponse:
            return web.FileResponse(self.asset)

        async def missing(_request: web.Request) -> web.StreamResponse:
            raise web.HTTPNotFound(text='nope')

        async def opinionated(_request: web.Request) -> web.StreamResponse:
            resp = web.Response(text='mine')
            resp.headers['Cache-Control'] = 'max-age=60'
            return resp

        app = web.Application(middlewares=[cache_middleware])
        app.add_routes([web.get('/page', page), web.get('/api', api), web.get('/file', file),
                        web.get('/missing', missing), web.get('/opinionated', opinionated)])
        app.router.add_static('/static', Path(tmp.name))
        return app

    async def _cc(self, path: str, **kwargs: object) -> str:
        resp = await self.client.get(path, **kwargs)                     # type: ignore[arg-type]
        return resp.headers.get('Cache-Control', '')

    @unittest_run_loop
    async def test_rendered_and_json_responses_are_never_stored(self) -> None:
        self.assertEqual(await self._cc('/page'), NO_STORE)
        self.assertEqual(await self._cc('/api'), NO_STORE)

    @unittest_run_loop
    async def test_files_revalidate_and_still_answer_304(self) -> None:
        """no-cache keeps the copy but re-asks: the ETag must survive to make that cheap."""
        resp = await self.client.get('/file')
        self.assertEqual(resp.headers['Cache-Control'], REVALIDATE)
        etag = resp.headers['ETag']
        again = await self.client.get('/file', headers={'If-None-Match': etag})
        self.assertEqual(again.status, 304)
        self.assertEqual(again.headers['Cache-Control'], REVALIDATE)

    @unittest_run_loop
    async def test_static_routes_are_covered_too(self) -> None:
        """add_static serves FileResponses — the app tier must match Caddy's edge rule."""
        self.assertEqual(await self._cc('/static/thing.css'), REVALIDATE)

    @unittest_run_loop
    async def test_an_error_response_is_stamped(self) -> None:
        """A cached 404 outlives the problem you then wrote — errors get the header too."""
        resp = await self.client.get('/missing')
        self.assertEqual(resp.status, 404)
        self.assertEqual(resp.headers['Cache-Control'], NO_STORE)

    @unittest_run_loop
    async def test_a_handler_that_set_its_own_header_keeps_it(self) -> None:
        self.assertEqual(await self._cc('/opinionated'), 'max-age=60')


if __name__ == '__main__':
    unittest.main()
