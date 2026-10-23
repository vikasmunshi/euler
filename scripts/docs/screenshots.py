#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Capture the site's main pages for the README, as one animated GIF that cycles through them.

Captures, signed out, the five main pages (`/`, `/solutions`, `/docs`, `/topics`, `/shell`)
and one random problem page below 100, with headless Chrome, and joins them into
`docs/screenshots.gif`: a frame per page, looping. A GIF plays wherever an image shows (GitHub
runs no script in a README) and the site's flat colours and text lose nothing to its 256
colours: each frame gets its own palette, undithered, so text stays crisp. The README shows it
between its `SCREENSHOTS` markers, which this script rewrites.

    python scripts/docs/screenshots.py                 # a random problem below 100
    python scripts/docs/screenshots.py --problem 2     # that one
    python scripts/docs/screenshots.py --base-url https://euler.example.com

Run it from the repository root, then commit `docs/screenshots.gif` and `README.md`.
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
GIF: Path = ROOT / 'docs' / 'screenshots.gif'
README: Path = ROOT / 'README.md'
BASE_URL: str = 'https://euler.vikasmunshi.com'

#: The browser window, in CSS pixels, captured at 1×: wide enough for the two-pane layout,
#: and text that stays sharp at the size a README shows it.
WINDOW: tuple[int, int] = (1600, 980)
#: How long each page stays up, in milliseconds.
FRAME_MS: int = 3000
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
    """One page to capture: its path on the site, and what to call it."""

    path: str
    title: str


def shots(problem: int) -> list[Shot]:
    """The pages, in the order the animation shows them."""
    return [
        Shot('/', 'Home'),
        Shot('/solutions/', 'Solutions'),
        Shot('/docs/', 'Docs'),
        Shot('/topics/', 'Topics'),
        Shot('/shell', 'Terminal'),
        Shot(f'/solutions/{problem}/', f'Problem {problem}'),
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
                            '--force-device-scale-factor=1', f'--virtual-time-budget={SETTLE_MS}',
                            f'--screenshot={target}', url],
                           check=True, capture_output=True, timeout=120)
        if target.is_file():
            with Image.open(target) as image:
                if ImageStat.Stat(image.convert('L')).mean[0] <= MAX_BRIGHTNESS:
                    return
        print(f'  retrying {url}: the capture is not the page')
    raise SystemExit(f'screenshots: no good capture of {url} in {ATTEMPTS} attempts')


def animate(frames: list[Path]) -> None:
    """Join *frames* into :data:`GIF`, looping, each with its own undithered palette."""
    images = [Image.open(f).convert('RGB').quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                                                    dither=Image.Dither.NONE)
              for f in frames]
    images[0].save(GIF, save_all=True, append_images=images[1:], duration=FRAME_MS, loop=0,
                   optimize=True, disposal=1)


def write_readme(all_shots: list[Shot]) -> None:
    """Show the animation in the README, between its SCREENSHOTS markers."""
    text = README.read_text(encoding='utf-8')
    if not _BLOCK_RE.search(text):
        raise SystemExit(f'screenshots: README.md has no {_START} … {_END} block')
    order = ' → '.join(f'<code>{s.path}</code>' for s in all_shots)
    block = (f'{_START}: written by scripts/docs/screenshots.py; edit the script, not this. -->\n'
             f'<p align="center"><img src="docs/screenshots.gif" width="100%" '
             f'alt="The web front end, signed out: {", ".join(s.title for s in all_shots)}"></p>\n'
             f'<p align="center">The web front end, signed out: {order}, '
             f'{FRAME_MS // 1000} seconds each.</p>\n'
             f'{_END}')
    README.write_text(_BLOCK_RE.sub(lambda _: block, text, count=1), encoding='utf-8')


def main(argv: list[str] | None = None) -> int:
    """Capture every page, animate them, and write the README block."""
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
    with tempfile.TemporaryDirectory() as scratch:
        frames = []
        for i, shot in enumerate(all_shots):
            frame = Path(scratch) / f'{i}.png'
            print(f'capturing {base_url}{shot.path}')
            capture(browser, f'{base_url}{shot.path}', frame)
            frames.append(frame)
        animate(frames)
    write_readme(all_shots)
    size = GIF.stat().st_size / 1e6
    print(f'wrote {GIF.relative_to(ROOT)} ({len(all_shots)} frames, {size:.1f} MB) and the README block')
    return 0


if __name__ == '__main__':
    sys.exit(main())
