#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Capture the site's main pages for the README: a screenshot carousel you click through.

Captures, signed out, the five main pages (`/`, `/solutions`, `/docs`, `/topics`, `/shell`)
and one random problem page below 100, with headless Chrome. GitHub runs no script in a
README, so the carousel is made of links: each screenshot is stored as a left and a right
half, shown side by side, and the left half links to the previous screenshot's page, the
right half to the next. Each screenshot has such a page under `docs/screenshots/`, and the
README shows the first between its `SCREENSHOTS` markers.

    python scripts/docs/screenshots.py                 # a random problem below 100
    python scripts/docs/screenshots.py --problem 2     # that one
    python scripts/docs/screenshots.py --base-url https://euler.example.com

Run it from the repository root, then commit `docs/screenshots/` and `README.md`.
"""
from __future__ import annotations

import argparse
import random
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageStat

ROOT: Path = Path(__file__).resolve().parents[2]
OUT_DIR: Path = ROOT / 'docs' / 'screenshots'
README: Path = ROOT / 'README.md'
BASE_URL: str = 'https://euler.vikasmunshi.com'

#: The browser window (CSS pixels) and the device scale: 1600 × 980 at 1.45 makes images
#: about 2320 × 1420, sharp on a high-density screen without being huge.
WINDOW: tuple[int, int] = (1600, 980)
SCALE: float = 1.45
#: Virtual time Chrome gives a page to settle (fonts, htmx swaps, MathJax) before the shot.
SETTLE_MS: int = 8000
#: The site is dark: a capture brighter than this (mean luminance, 0–255) is not the page.
#: Headless Chrome now and then paints a stray resource instead, the logo on white.
MAX_BRIGHTNESS: float = 90
ATTEMPTS: int = 3

_START = '<!-- SCREENSHOTS:START'
_END = '<!-- SCREENSHOTS:END -->'
_BLOCK_RE = re.compile(rf'{re.escape(_START)}.*?{re.escape(_END)}', re.DOTALL)


@dataclass(frozen=True)
class Shot:
    """One page to capture: its file stem, its path on the site, and what to call it."""

    stem: str
    path: str
    title: str

    def half(self, side: str) -> str:
        """The file name of this shot's *side* (`left` / `right`) half."""
        return f'{self.stem}-{side}.png'


def shots(problem: int) -> list[Shot]:
    """The pages, in carousel order."""
    return [
        Shot('01-home', '/', 'Home'),
        Shot('02-solutions', '/solutions/', 'Solutions'),
        Shot('03-docs', '/docs/', 'Docs'),
        Shot('04-topics', '/topics/', 'Topics'),
        Shot('05-shell', '/shell', 'Terminal'),
        Shot('06-problem', f'/solutions/{problem}/', f'Problem {problem}'),
    ]


def chrome() -> str:
    """The headless browser to drive: Chrome, or Chromium."""
    for name in ('google-chrome', 'chromium', 'chromium-browser'):
        if path := shutil.which(name):
            return path
    raise SystemExit('screenshots: no google-chrome or chromium on PATH (make install-chrome)')


def capture(browser: str, url: str, target: Path) -> None:
    """Screenshot *url* to *target*, signed out (a fresh profile has no session cookie).

    Retried when the result is missing or too bright to be the site (:data:`MAX_BRIGHTNESS`).
    """
    for _ in range(ATTEMPTS):
        target.unlink(missing_ok=True)
        with tempfile.TemporaryDirectory() as profile:
            subprocess.run([browser, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                            f'--user-data-dir={profile}', f'--window-size={WINDOW[0]},{WINDOW[1]}',
                            f'--force-device-scale-factor={SCALE}', f'--virtual-time-budget={SETTLE_MS}',
                            f'--screenshot={target}', url],
                           check=True, capture_output=True, timeout=120)
        if target.is_file():
            with Image.open(target) as image:
                if ImageStat.Stat(image.convert('L')).mean[0] <= MAX_BRIGHTNESS:
                    return
        print(f'  retrying {url}: the capture is not the page')
    raise SystemExit(f'screenshots: no good capture of {url} in {ATTEMPTS} attempts')


def split(full: Path, shot: Shot) -> None:
    """Save *full* as the shot's two halves in :data:`OUT_DIR`."""
    with Image.open(full) as image:
        middle = image.width // 2
        for side, box in (('left', (0, 0, middle, image.height)),
                          ('right', (middle, 0, image.width, image.height))):
            image.crop(box).save(OUT_DIR / shot.half(side), optimize=True)


def carousel(shot: Shot, prev: Shot, nxt: Shot, prefix: str, page: str) -> str:
    """The two halves, linked: left → *prev*'s page, right → *nxt*'s.

    *prefix* is the path from the including file to the images, *page* to the pages. No
    whitespace between the tags, so the halves meet with no gap.
    """
    left = (f'<a href="{page}{prev.stem}.md" title="Previous: {prev.title}">'
            f'<img src="{prefix}{shot.half("left")}" width="50%" alt="{shot.title}, left half"></a>')
    right = (f'<a href="{page}{nxt.stem}.md" title="Next: {nxt.title}">'
             f'<img src="{prefix}{shot.half("right")}" width="50%" alt="{shot.title}, right half"></a>')
    return f'<p align="center">{left}{right}</p>'


def caption(index: int, total: int, shot: Shot, base_url: str) -> str:
    """The line under a screenshot: where it is in the carousel, and the page it shows."""
    return (f'<p align="center"><b>{index} / {total} · {shot.title}</b> '
            f'(<a href="{base_url}{shot.path}"><code>{shot.path}</code></a>), signed out. '
            f'Click the left half for the previous page, the right half for the next.</p>')


def write_pages(all_shots: list[Shot], base_url: str) -> None:
    """One page per screenshot under :data:`OUT_DIR`, each linked to its neighbours."""
    total = len(all_shots)
    for i, shot in enumerate(all_shots):
        prev, nxt = all_shots[i - 1], all_shots[(i + 1) % total]
        (OUT_DIR / f'{shot.stem}.md').write_text(
            f'## Screenshots: {shot.title}\n\n'
            f'{carousel(shot, prev, nxt, "", "")}\n\n'
            f'{caption(i + 1, total, shot, base_url)}\n\n'
            f'[Back to the README](../../README.md)\n', encoding='utf-8')


def write_readme(all_shots: list[Shot], base_url: str) -> None:
    """Show the first screenshot in the README, between its SCREENSHOTS markers."""
    text = README.read_text(encoding='utf-8')
    if not _BLOCK_RE.search(text):
        raise SystemExit(f'screenshots: README.md has no {_START} … {_END} block')
    first, total = all_shots[0], len(all_shots)
    block = (f'{_START}: written by scripts/docs/screenshots.py; edit the script, not this. -->\n'
             f'{carousel(first, all_shots[-1], all_shots[1], "docs/screenshots/", "docs/screenshots/")}\n'
             f'{caption(1, total, first, base_url)}\n'
             f'{_END}')
    README.write_text(_BLOCK_RE.sub(lambda _: block, text, count=1), encoding='utf-8')


def main(argv: list[str] | None = None) -> int:
    """Capture every page, split it, and write the carousel's pages and the README block."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument('--problem', type=int, default=None,
                        help='the problem page to capture (default: a random one below 100)')
    parser.add_argument('--base-url', default=BASE_URL, help=f'the site to capture (default: {BASE_URL})')
    args = parser.parse_args(argv)
    problem = args.problem if args.problem is not None else random.randint(1, 99)
    if not 1 <= problem <= 99:
        parser.error('--problem must be below 100: only those pages are public')
    base_url = args.base_url.rstrip('/')

    browser = chrome()
    all_shots = shots(problem)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob('*'):           # a rerun replaces the set, never mixes two
        old.unlink()
    with tempfile.TemporaryDirectory() as scratch:
        for shot in all_shots:
            full = Path(scratch) / f'{shot.stem}.png'
            print(f'capturing {base_url}{shot.path}')
            capture(browser, f'{base_url}{shot.path}', full)
            split(full, shot)
    write_pages(all_shots, base_url)
    write_readme(all_shots, base_url)
    print(f'wrote {len(all_shots)} screenshots to {OUT_DIR.relative_to(ROOT)}/ and the README block')
    return 0


if __name__ == '__main__':
    sys.exit(main())
