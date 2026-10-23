#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Versioned asset URLs: every asset a template names carries a hash of its bytes, and only
an existing file gets one (euler_site.assets; docs/web-server-guide.md § 11.10)."""
from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

from euler_site import assets

_PACKAGE = Path(assets.__file__).resolve().parent
_TEMPLATE_DIRS = (_PACKAGE / 'templates', _PACKAGE / 'site' / 'templates')
#: A bare asset URL in markup — what the edge must revalidate on every use.
_BARE = re.compile(r'''(?:href|src)=["']/(?:assets|vendor)/''')
_NAMED = re.compile(r'''asset\(\s*'([^']+)'\s*\)''')


def _templates() -> list[Path]:
    return sorted(p for d in _TEMPLATE_DIRS for p in d.glob('*.html'))


class AssetUrlTests(unittest.TestCase):
    def test_a_file_is_named_by_its_contents(self) -> None:
        digest = hashlib.sha256((assets.CONTENT_DIR / 'assets/site.css').read_bytes()).hexdigest()
        self.assertEqual(assets.asset_url('/assets/site.css'), f'/assets/site.css?v={digest[:12]}')

    def test_a_missing_file_keeps_its_bare_path(self) -> None:
        self.assertEqual(assets.asset_url('/assets/no-such-file.js'), '/assets/no-such-file.js')


class TemplateTests(unittest.TestCase):
    def test_no_template_writes_a_bare_asset_url(self) -> None:
        for path in _templates():
            with self.subTest(template=path.name):
                self.assertIsNone(_BARE.search(path.read_text(encoding='utf-8')),
                                  "write {{ asset('/assets/…') }}, not the bare path")

    def test_every_named_asset_exists(self) -> None:
        named = {(p.name, m) for p in _templates() for m in _NAMED.findall(p.read_text(encoding='utf-8'))}
        self.assertTrue(named)
        for template, url in sorted(named):
            with self.subTest(template=template, url=url):
                self.assertTrue((assets.CONTENT_DIR / url.lstrip('/')).is_file())


if __name__ == '__main__':
    unittest.main()
