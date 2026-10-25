#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The site's two themes and its narrow layout, read from the files that implement them.

Both live in the browser: site.js picks the theme before the first paint and keeps the
terminal's iframe, the editor and other tabs in step; site.css stacks the panes on a narrow
screen, and site.js starts the terminal hidden there. What a unit test can hold is the
wiring between those files — one storage key, one breakpoint, one event, every token defined
in both palettes — which is exactly what drifts when one side is edited without the other.
The rendering itself was verified in headless Chrome (web-server-guide § The site).
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

_SITE = Path(__file__).resolve().parents[1] / 'packages' / 'site' / 'euler_site'
_ASSETS = _SITE / 'content' / 'assets'


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _block(css: str, selector: str) -> str:
    """Every declaration in the rule blocks whose selector is exactly *selector*."""
    return ''.join(re.findall(re.escape(selector) + r' \{([^}]*)\}', css))


class ThemeTests(unittest.TestCase):
    """Light and dark: one set of tokens, two palettes, one choice shared everywhere."""

    css: str = _read(_ASSETS / 'site.css')
    site_js: str = _read(_ASSETS / 'site.js')

    def test_the_light_palette_redefines_every_colour_token(self) -> None:
        """A colour token the light block forgets keeps its dark value on the light ground —
        a near-white text token on white is the failure this guards."""
        dark = dict(re.findall(r'(--[a-z0-9-]+):\s*([^;]+);', _block(self.css, ':root')))
        light = dict(re.findall(r'(--[a-z0-9-]+):\s*([^;]+);', _block(self.css, ':root[data-theme="light"]')))
        literal = {name for name, value in dark.items() if re.match(r'#|rgba?\(|color-mix', value)
                   and 'var(--' not in value}
        self.assertTrue(literal)
        self.assertEqual(sorted(literal - light.keys()), [],
                         'these colour tokens have no light value')

    def test_both_palettes_declare_their_color_scheme(self) -> None:
        """So the browser's own controls (scrollbars, checkboxes, form fields) match."""
        self.assertIn('color-scheme: dark', _block(self.css, ':root'))
        self.assertIn('color-scheme: light', _block(self.css, ':root[data-theme="light"]'))

    def test_the_theme_is_set_before_anything_else_in_site_js(self) -> None:
        """site.js loads from <head> without defer; the theme must be its first act, or the
        page paints the wrong ground first."""
        self.assertLess(self.site_js.index("applyTheme(storedTheme() || systemTheme());"),
                        self.site_js.index('var MJ_TEX'))

    def test_the_site_and_the_code_viewer_share_one_choice(self) -> None:
        """One toggle, two places: a choice made on /code/ holds on the site and back."""
        key = re.search(r"var THEME_KEY = '([^']+)'", self.site_js)
        assert key is not None
        self.assertIn(f"var KEY = '{key.group(1)}'", _read(_ASSETS / 'code.js'))

    def test_the_header_carries_the_toggle_site_js_wires(self) -> None:
        nav = _read(_SITE / 'site' / 'templates' / '_nav.html')
        self.assertIn('data-theme-toggle', nav)
        self.assertIn("'[data-theme-toggle]'", self.site_js)

    def test_the_terminal_and_the_editor_follow_a_toggle(self) -> None:
        """Neither is CSS: xterm's colours and CodeMirror's theme are options, so each must
        listen for the event site.js announces every theme change with."""
        self.assertIn("new CustomEvent('euler:theme'", self.site_js)
        terminal = _read(_ASSETS / 'terminal.js')
        self.assertIn("addEventListener('euler:theme'", terminal)
        self.assertIn('minimumContrastRatio', terminal)     # the shell paints for a dark ground
        editor = _read(_ASSETS / 'editor.js')
        self.assertIn("addEventListener('euler:theme'", editor)
        self.assertIn('reconfigure', editor)

    def test_a_toggle_reaches_the_terminal_frame_by_storage_event(self) -> None:
        """The frame is its own document; the `storage` event is what crosses into it."""
        self.assertIn("addEventListener('storage'", self.site_js)
        self.assertIn('site.js', _read(_SITE / 'site' / 'templates' / 'terminal.html'))


class NarrowLayoutTests(unittest.TestCase):
    """≤ 820px: the panes stack, content above the terminal, and the terminal starts hidden."""

    css: str = _read(_ASSETS / 'site.css')
    site_js: str = _read(_ASSETS / 'site.js')

    def test_css_and_js_agree_on_the_breakpoint(self) -> None:
        """The CSS stacks the panes and the JS hides the terminal at the same width, or a
        band of widths gets one without the other."""
        self.assertIn('@media (max-width: 820px)', self.css)
        self.assertIn("matchMedia('(max-width: 820px)')", self.site_js)

    def test_one_pane_at_a_time_the_terminal_over_the_content(self) -> None:
        """Split, neither half of a phone is usable — a terminal a dozen rows tall least of
        all — so a shown terminal takes the whole pane area, and hiding it is the way back."""
        narrow = self.css.split('@media (max-width: 820px)')[1]
        self.assertIn('grid-template-rows: minmax(0, 1fr);', narrow)
        self.assertNotIn('minmax(0, 1fr) minmax(0, 1fr)', narrow)
        self.assertIn('body:not(.ws-hidden):not(.is-signin):not(.is-dialogue) .pane-content '
                      '{ display: none; }', narrow)

    def test_a_pane_that_moves_hides_the_narrow_terminal(self) -> None:
        """The page asked for is under the terminal. Only a move, though: a re-render of the
        same page (a refresh, a nudge from the shell) must not pull the terminal away, nor
        may a control that asks for the terminal as well as a page."""
        hook = self.site_js.split('var landedPath')[1].split('\n  });')[0]
        self.assertIn('path !== landedPath', hook)
        self.assertIn("closest('[data-term-show]')", hook)
        self.assertIn('isNarrow()', hook)
        self.assertIn('setWsHidden(true)', hook)

    def test_fields_are_large_enough_that_ios_does_not_zoom(self) -> None:
        """iOS zooms into a focused field under 16px and stays zoomed; the 13px root puts
        every field there."""
        narrow = self.css.split('@media (max-width: 820px)')[1]
        rule = re.search(r'body :is\(([^{]*)\) \{\s*font-size: 16px;', narrow)
        assert rule is not None, 'no 16px rule for form fields at narrow width'
        for kind in ('input', 'textarea', 'select', 'contenteditable'):
            self.assertIn(kind, rule.group(1))

    def test_the_narrow_terminal_flag_is_never_stored(self) -> None:
        """A phone starts every document with the terminal hidden; showing it there must not
        change what a wide screen remembers."""
        set_hidden = self.site_js.split('function setWsHidden(on) {')[1].split('\n  }')[0]
        narrow_branch, _, wide_branch = set_hidden.partition('return; }')
        self.assertIn('narrowHidden = on', narrow_branch)
        self.assertNotIn('localStorage', narrow_branch)
        self.assertIn('localStorage', wide_branch)
        self.assertIn('var narrowHidden = true;', self.site_js)

    def test_login_goes_to_the_form_only_while_it_is_on_screen(self) -> None:
        """The header's Login focuses the right pane's sign-in form instead of navigating.
        The narrow layout hides that pane, and focusing a hidden field does nothing — which
        left a phone with a Login that went nowhere. It must navigate to /login there."""
        handler = self.site_js.split("closest('a[data-login]')")[1].split('}, true);')[0]
        self.assertIn('email.getClientRects().length', handler)

    def test_the_section_strip_gives_way_to_the_header_nav(self) -> None:
        """On a phone the strip is four stacked tiles repeating the header nav's links."""
        narrow = self.css.split('@media (max-width: 820px)')[1]
        self.assertIn('.cards.sections { display: none; }', narrow)

    def test_each_page_kind_says_which_pane_leads(self) -> None:
        """Signed out, the right pane is either the way in (hidden: the pill offers it) or,
        on the auth pages, the page itself (shown instead of the content)."""
        base = _read(_SITE / 'site' / 'templates' / 'base.html')
        self.assertIn('{% block body_class %}{% if not subject %}is-signin{% endif %}', base)
        self.assertIn('is-dialogue', _read(_SITE / 'templates' / 'auth_base.html'))
        self.assertIn('is-signin', _read(_SITE / 'templates' / 'terms.html'))   # a document
        narrow = self.css.split('@media (max-width: 820px)')[1]
        self.assertIn('body.is-signin .pane-ws { display: none; }', narrow)
        self.assertIn('body.is-dialogue .pane-content { display: none; }', narrow)


if __name__ == '__main__':
    unittest.main()
