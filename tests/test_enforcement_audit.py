#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The enforcement audit (docs/authorizations.md § Where it is enforced) covers every
`maintainer` and `admin` command, at its declared floor: a new privileged command fails here
until someone has written down what, besides the floor, stops a lesser profile."""
from __future__ import annotations

import importlib
import re
import unittest
from pathlib import Path

from solver.shell.command import registry
from solver.utils.loader import load_commands
from tests import silence

silence()

_DOC = Path(__file__).resolve().parents[1] / 'docs' / 'authorizations.md'
_SECTION = '## Where it is enforced'
_ROW = re.compile(r'^\| `([^`]+)` \| (\w+) \|')
_PRIVILEGED = ('maintainer', 'admin')


def _audited() -> dict[str, str]:
    """The audit table's rows: command → the floor it records."""
    text = _DOC.read_text(encoding='utf-8')
    section = text[text.index(_SECTION):]
    return {m.group(1): m.group(2) for line in section.splitlines() if (m := _ROW.match(line))}


class EnforcementAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # The host's whole command set: the solver's own, and what the web host's extension
        # loads. This process is the owner → admin, so nothing is withheld.
        load_commands()
        from euler_webshell.shell import HOST_COMMANDS
        for module in HOST_COMMANDS:
            importlib.import_module(module)

    def test_every_privileged_command_is_audited_at_its_floor(self) -> None:
        live = {cmd.name: cmd.requires for cmd in registry.all() if cmd.requires in _PRIVILEGED}
        self.assertTrue(live)
        self.assertEqual(_audited(), live)


if __name__ == '__main__':
    unittest.main()
