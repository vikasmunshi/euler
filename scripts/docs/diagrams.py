#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Capture the presentation's architecture diagrams as images for the guides and the README.

The deck (`docs/presentation/`) draws each diagram once, in HTML and CSS; the guides embed
the same picture rather than a second drawing that would drift from it. Every element marked
`data-figure="<name>"` in the deck is opened alone (`index.html?figure=<name>` hides the rest
of its slide), captured with headless Chrome at 2×, trimmed to the diagram, and written to
`docs/diagrams/<name>.png`. No server: the deck is read straight from the working tree.

    python scripts/docs/diagrams.py             # every figure
    python scripts/docs/diagrams.py web keychain

Run it from the repository root after changing a diagram on its slide, then commit
`docs/diagrams/`.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

ROOT: Path = Path(__file__).resolve().parents[2]
DECK: Path = ROOT / 'docs' / 'presentation' / 'index.html'
OUT: Path = ROOT / 'docs' / 'diagrams'

#: The deck's own stage, in CSS pixels: one slide fills it exactly.
WINDOW: tuple[int, int] = (1600, 900)
#: Device pixels per CSS pixel: sharp on a high-density screen, still small as a PNG.
SCALE: int = 2
#: Margin left around the trimmed diagram, in device pixels.
PAD: int = 48
#: Virtual time for fonts and the deck's own layout before the shot.
SETTLE_MS: int = 3000
#: The developer section's background (`--dev-bg` in deck.css), which the trim removes.
BACKGROUND: tuple[int, int, int] = (0x18, 0x18, 0x1B)
#: How far a pixel may stray from :data:`BACKGROUND` and still count as background.
TOLERANCE: int = 12

_FIGURE_RE = re.compile(r'data-figure="([\w-]+)"')


def figures() -> list[str]:
    """Every figure the deck marks, in slide order."""
    return _FIGURE_RE.findall(DECK.read_text(encoding='utf-8'))


def chrome() -> str:
    """The headless browser to drive: Chrome, or Chromium."""
    for name in ('google-chrome', 'chromium', 'chromium-browser'):
        if path := shutil.which(name):
            return path
    raise SystemExit('diagrams: no google-chrome or chromium on PATH (make install-chrome)')


def capture(browser: str, name: str, target: Path) -> None:
    """Screenshot figure *name*, alone on its slide, to *target*."""
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run([browser, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                        f'--user-data-dir={profile}', f'--window-size={WINDOW[0]},{WINDOW[1]}',
                        f'--force-device-scale-factor={SCALE}', f'--virtual-time-budget={SETTLE_MS}',
                        f'--screenshot={target}', f'{DECK.as_uri()}?figure={name}'],
                       check=True, capture_output=True, timeout=120)
    if not target.is_file():
        raise SystemExit(f'diagrams: no capture of {name}')


def trim(source: Path, target: Path) -> tuple[int, int]:
    """Crop *source* to its diagram plus :data:`PAD`, save it as *target*, and return its size."""
    with Image.open(source) as shot:
        image = shot.convert('RGB')
    ground = Image.new('RGB', image.size, BACKGROUND)
    mask = ImageChops.difference(image, ground).convert('L').point(lambda v: 255 if v > TOLERANCE else 0)
    box = mask.getbbox()
    if box is None:
        raise SystemExit(f'diagrams: {source.name} is blank; is data-figure on a visible element?')
    left, top, right, bottom = box
    image = image.crop((max(0, left - PAD), max(0, top - PAD),
                        min(image.width, right + PAD), min(image.height, bottom + PAD)))
    image.save(target, optimize=True)
    return image.width, image.height


def main(argv: list[str] | None = None) -> int:
    """Capture the named figures, or every one, into :data:`OUT`."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument('names', nargs='*', help='the figures to capture (default: every one in the deck)')
    args = parser.parse_args(argv)
    known = figures()
    names = args.names or known
    if unknown := sorted(set(names) - set(known)):
        parser.error(f'no data-figure {", ".join(unknown)} in the deck (it has: {", ".join(known)})')

    browser = chrome()
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as scratch:
        for name in names:
            shot = Path(scratch) / f'{name}.png'
            capture(browser, name, shot)
            target = OUT / f'{name}.png'
            width, height = trim(shot, target)
            print(f'wrote {target.relative_to(ROOT)} ({width}×{height}, {target.stat().st_size / 1e3:.0f} kB)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
