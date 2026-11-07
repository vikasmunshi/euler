#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The account icon: what a signed-in user wears on the account page and in the header.

docs/web-server-guide.md § The site, Account. A user picks one of :data:`STANDARD` or uploads
an image. The choice is per-user state, kept beside the shell's under `.state/<slug>/` in their
own clone, so it needs no service of its own and no one else's permission to change.

An upload is held to raster formats recognised by their leading bytes, whatever the browser
claims. SVG is refused on purpose: it can carry script, and the stored bytes are served back
under this origin. The browser scales an image down before sending it (site.js), which also
strips its metadata; the size cap here is for whatever did not come through that path.
"""
from __future__ import annotations

__all__ = ['DEFAULT', 'Icon', 'IMAGE_FILE', 'MAX_IMAGE', 'STANDARD', 'read', 'save_image', 'save_standard']

import hashlib
import os
from pathlib import Path
from typing import NamedTuple

from markupsafe import Markup

from euler_site.store import load_json, save_json

#: The stored choice, and the stored upload, in the user's state directory.
_CHOICE_FILE: str = 'icon.json'
IMAGE_FILE: str = 'icon.image'
#: Largest upload kept. The scaled image site.js sends is a small fraction of this.
MAX_IMAGE: int = 256 * 1024

#: A letter of the kind the problems are written in, drawn in the page's own serif.
_LETTER: str = ('<text x="12" y="18" text-anchor="middle" font-family="serif" font-size="19" '
                'fill="currentColor">{}</text>')
_SHAPE: str = '<path fill="currentColor" d="{}"/>'

#: The standard icons: name → the body of a 24×24 `<svg>`, drawn in `currentColor`.
STANDARD: dict[str, str] = {
    'person': _SHAPE.format('M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0 2c-4.42 0-8 2.24-8 5v1h16v-1c0-2.76-3.58-5-8-5Z'),
    'sigma': _LETTER.format('Σ'),
    'pi': _LETTER.format('π'),
    'phi': _LETTER.format('φ'),
    'lambda': _LETTER.format('λ'),
    'infinity': _LETTER.format('∞'),
    'integral': _LETTER.format('∫'),
    'star': _SHAPE.format('M12 2l3 6.9 7.5.7-5.7 4.9 1.7 7.3L12 18l-6.5 3.8 1.7-7.3L1.5 9.6 9 8.9z'),
    'hexagon': _SHAPE.format('M12 2l8.7 5v10L12 22l-8.7-5V7z'),
    'triangle': _SHAPE.format('M12 3l10 18H2z'),
    'diamond': _SHAPE.format('M12 2l10 10-10 10L2 12z'),
    'bolt': _SHAPE.format('M13 2L4 14h7l-1 8 9-12h-7z'),
}


class Icon(NamedTuple):
    """A user's icon: a standard one by *name*, or an image by its media *type* and *version*."""

    name: str = 'person'
    type: str = ''
    #: The image's content hash: the `?v=` of its URL, so a new image is a new URL.
    version: str = ''

    @property
    def svg(self) -> Markup:
        """The body of the standard icon's `<svg>`, which is this module's own markup."""
        return Markup(STANDARD[self.name])


DEFAULT: Icon = Icon()


_PNG, _JPEG, _WEBP = 'image/png', 'image/jpeg', 'image/webp'


def _media_type(data: bytes) -> str:
    """The media type *data* opens with, or '' when it is not an image kept here."""
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return _PNG
    if data.startswith(b'\xff\xd8\xff'):
        return _JPEG
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return _WEBP
    return ''


def read(state_dir: Path) -> Icon:
    """The icon stored in *state_dir*, or :data:`DEFAULT` for none or for one that no longer stands."""
    choice = load_json(state_dir / _CHOICE_FILE)
    version, media_type = str(choice.get('version', '')), str(choice.get('type', ''))
    if version and media_type in (_PNG, _JPEG, _WEBP) and (state_dir / IMAGE_FILE).is_file():
        return Icon(type=media_type, version=version)
    name = str(choice.get('name', ''))
    return Icon(name=name) if name in STANDARD else DEFAULT


def save_standard(state_dir: Path, name: str) -> str:
    """Choose the standard icon *name*, dropping any image. Returns why not, or ''."""
    if name not in STANDARD:
        return 'That is not one of the standard icons.'
    state_dir.mkdir(parents=True, exist_ok=True)
    save_json(state_dir / _CHOICE_FILE, {'name': name})
    (state_dir / IMAGE_FILE).unlink(missing_ok=True)
    return ''


def save_image(state_dir: Path, data: bytes) -> str:
    """Keep *data* as the user's icon. Returns why not, or ''."""
    if not data:
        return 'Choose an image to upload.'
    if len(data) > MAX_IMAGE:
        return f'That image is too large: the limit is {MAX_IMAGE // 1024} KB.'
    media_type = _media_type(data)
    if not media_type:
        return 'That file is not a PNG, JPEG or WebP image.'
    state_dir.mkdir(parents=True, exist_ok=True)
    staged = state_dir / f'{IMAGE_FILE}.new'
    staged.write_bytes(data)
    os.replace(staged, state_dir / IMAGE_FILE)
    save_json(state_dir / _CHOICE_FILE, {'type': media_type, 'version': hashlib.sha256(data).hexdigest()[:12]})
    return ''
