#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The message spool as the carrier of the solver shell's notices (:mod:`solver.core.notices`)."""
from __future__ import annotations

__all__ = ['HOST_KEY_HINT', 'WEB_KEY_HINT', 'Spool']

from dataclasses import dataclass

from euler_webshell.msg.notify import dismiss_by_subject, notify_staff

#: Over the web the reader is looking at the page: the envelope chip in the header, whose key row
#: carries its own save button, so nobody has to type a message id they would have to find first.
WEB_KEY_HINT: str = ('open the [accent]✉ messages[/accent] menu in the header and press '
                     '[accent]save[/accent] on the master-key message.')
#: A terminal has no header — there, the verbs are the only answer there is.
HOST_KEY_HINT: str = 'run [accent]msg list[/accent], then [accent]msg act <id>[/accent].'


@dataclass(frozen=True)
class Spool:
    """Deliver notices through the spool; *hint* names where a waiting key is taken."""
    hint: str

    def to_staff(self, subject: str, body: str) -> bool:
        return notify_staff(subject, body)

    def dismiss(self, subject: str) -> bool:
        return dismiss_by_subject(subject) > 0

    def key_hint(self) -> str:
        return self.hint
