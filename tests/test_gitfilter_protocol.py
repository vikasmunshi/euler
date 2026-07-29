#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The crypt filter's behaviour when it cannot get the master key.

A real git repository, a really wired filter, and a really absent key — because the bug this
pins was invisible to every unit-level test and cost three rounds of debugging on a live host.

The filter used to `return 1` **before the protocol handshake** when the key was unavailable.
git sees a filter process that dies on startup and reports `fatal: the remote end hung up
unexpectedly` — a transport failure, which `filter.<name>.required=false` cannot soften,
because there is no filter *result* to fall back from. So a collaborator whose vault was
locked (the normal state outside their own session: `~/.euler/id` is vault-encrypted and the
session key lives in their tmpfs) could not check anything out at all, and the operator's
`reset-user.sh --no-filter` — written precisely for that case — failed identically.

It now completes the handshake and answers `status=abort`, the protocol's own word for "not
this file, and not any after it". With the filter not required, git falls back to the stored
content and the checkout succeeds — ciphertext in the worktree, which is exactly the state an
un-authorized clone is designed to sit in.

Hermetic: a throwaway repo under a temp dir, whose sibling secrets dir never exists, so the
key really cannot be loaded. Nothing here touches the operator's own tree or key material.
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

_SOURCE_ROOT = Path(__file__).resolve().parents[1]


def _git_available() -> bool:
    try:
        return subprocess.run(['git', '--version'], capture_output=True).returncode == 0
    except OSError:
        return False


@unittest.skipUnless(_git_available(), 'git is not installed')
class LockedKeyCheckoutTests(unittest.TestCase):
    """A wired filter with no reachable key must not make git fatal."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name) / 'repo'
        self.repo.mkdir()
        # The filter derives its secrets dir as <repo>.parent/.<repo.name> — never created
        # here, so `load_private_key` raises FileNotFoundError: the key is genuinely absent,
        # which is the same _KEY_ERRORS path a locked vault takes.
        self.env = {**os.environ, 'EULER_REPO_ROOT': str(self.repo),
                    'PYTHONPATH': str(_SOURCE_ROOT), 'GIT_TERMINAL_PROMPT': '0'}
        for key in ('EULER_VAULT_KEY_FILE', 'EULER_VAULT_PASSWORD'):
            self.env.pop(key, None)
        self._git('init', '-q', '-b', 'master')
        self._git('config', 'user.email', 't@example.com')
        self._git('config', 'user.name', 'T')
        (self.repo / '.gitattributes').write_text('secret/** filter=solver-crypt -text -diff\n')
        (self.repo / 'secret').mkdir()
        (self.repo / 'secret' / 'answer.txt').write_text('the plaintext\n')

    def _git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(['git', *args], cwd=self.repo, env=self.env,
                                capture_output=True, text=True)
        if check:
            self.assertEqual(result.returncode, 0, f'git {" ".join(args)}: {result.stderr}')
        return result

    def _wire(self, *, required: bool) -> None:
        """Wire the filter exactly as `gitfilter install` does — including -P."""
        base = f'{sys.executable} -P -m solver.crypto.gitfilter'
        self._git('config', 'filter.solver-crypt.process', f'{base} process')
        self._git('config', 'filter.solver-crypt.clean', f'{base} clean')
        self._git('config', 'filter.solver-crypt.smudge', f'{base} smudge')
        self._git('config', 'filter.solver-crypt.required', 'true' if required else 'false')

    def test_an_unrequired_filter_with_no_key_still_checks_out(self) -> None:
        """The `--no-filter` contract: content passes through, git succeeds.

        Before the fix this failed with `fatal: the remote end hung up unexpectedly`, because
        the filter died at startup rather than answering.
        """
        self._wire(required=False)
        self._git('add', '-A')
        self._git('commit', '-qm', 'init')
        (self.repo / 'secret' / 'answer.txt').unlink()
        result = self._git('checkout', '--', 'secret', check=False)
        self.assertEqual(result.returncode, 0, f'checkout should degrade, not die: {result.stderr}')
        self.assertNotIn('hung up unexpectedly', result.stderr)
        self.assertTrue((self.repo / 'secret' / 'answer.txt').exists(), 'the file must be restored')

    def test_a_required_filter_with_no_key_fails_as_a_filter_not_as_a_transport(self) -> None:
        """Required means the checkout must fail — but on the filter's terms.

        The distinction is not cosmetic: `required=false` can only rescue a filter that
        *answered*, so a filter that dies leaves the operator with no way through at all.
        """
        # Commit while the filter may fall back — with it required, even `git add` refuses,
        # which is itself the correct behaviour and not what this test is about.
        self._wire(required=False)
        self._git('add', '-A')
        self._git('commit', '-qm', 'init')
        self._git('config', 'filter.solver-crypt.required', 'true')
        (self.repo / 'secret' / 'answer.txt').unlink()
        result = self._git('checkout', '--', 'secret', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('cannot load master key', result.stderr, 'the filter must say why')


if __name__ == '__main__':
    unittest.main()
