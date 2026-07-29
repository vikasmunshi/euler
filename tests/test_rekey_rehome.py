#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""A clone that saves a rotated key must end up somewhere it can read.

The bug this pins was reported from a live web shell and is a genuine trap rather than a
missing branch. A rotation re-encrypts every tracked private blob, so the moment a
collaborator runs `msg save` their own HEAD stops decrypting — and *every* way out of that
goes through HEAD. `git stash` materialises it, so `git-sync` cannot even reach its merge:
the smudge filter raises `InvalidTag`, git calls the sync fatal, and the clone is stuck
being stale with no self-service repair.

So the tests here build the wedge for real — real X25519 keys, a real wired filter, a real
rotation, a real bare origin — and assert that the clone lands on the re-encrypted tree with
its own edits intact. A mocked git would prove nothing: the failure is entirely about which
commands touch HEAD.

Hermetic: a throwaway repo under a temp dir with its own secrets dir, never the operator's.
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from importlib import import_module
from json import dumps
from pathlib import Path
from secrets import token_bytes
from tempfile import TemporaryDirectory
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from solver.crypto.ciphers import enc_key_payload, load_private_key, read_master_key
from solver.crypto.config import config as crypto_config
from tests import silence

silence()  # the repair narrates what it is doing; the assertions are the record here

_SOURCE_ROOT = Path(__file__).resolve().parents[1]

#: One private solution, and the plaintext that must survive the whole exercise.
_SOLUTION = 'solutions/private/p0100_0199/p0101/p0101_s0.py'
_PLAINTEXT = "from solver.runners import runner\n\n\n@runner.main\ndef solve() -> str:\n    return '1'\n"


def _git_available() -> bool:
    try:
        return subprocess.run(['git', '--version'], capture_output=True).returncode == 0
    except OSError:
        return False


@unittest.skipUnless(_git_available(), 'git is not installed')
class RotationRehomeTests(unittest.TestCase):
    """`msg save` on a stale clone: HEAD is unreadable, and the repair is origin/master."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.repo, self.secrets = root / 'repo', root / '.repo'
        self.origin = root / 'origin.git'
        self.secrets.mkdir(mode=0o700)
        self.repo.mkdir()

        # A real keypair in a real machine-local secrets dir: the filter subprocess finds it
        # by deriving <repo>.parent/.<repo.name>, which is why the names above are not free.
        self.private_key = X25519PrivateKey.generate()
        (self.secrets / 'id').write_bytes(self.private_key.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
        self.env = {**os.environ, 'EULER_REPO_ROOT': str(self.repo),
                    'PYTHONPATH': str(_SOURCE_ROOT), 'GIT_TERMINAL_PROMPT': '0'}
        for key in ('EULER_VAULT_KEY_FILE', 'EULER_VAULT_PASSWORD'):
            self.env.pop(key, None)

        # The module-level config objects are what the code under test reads; point both at
        # the throwaway tree for the duration, and clear the master-key cache around it.
        self._patch_config()
        self.write_master_key(token_bytes(32))

        subprocess.run(['git', 'init', '-q', '--bare', str(self.origin)], check=True)
        self._git('init', '-q', '-b', 'master')
        self._git('config', 'user.email', 't@example.com')
        self._git('config', 'user.name', 'T')
        self._git('remote', 'add', 'origin', str(self.origin))
        (self.repo / '.gitattributes').write_text(
            'solutions/private/** filter=solver-crypt -text -diff\n')
        self._wire()
        self.solution = self.repo / _SOLUTION
        self.solution.parent.mkdir(parents=True)
        self.solution.write_text(_PLAINTEXT)
        self._git('add', '-A')
        self._git('commit', '-qm', 'the tree before the rotation')
        self._git('push', '-q', 'origin', 'master')

    def _patch_config(self) -> None:
        """Redirect the crypto dict and `config.root_dir` at the throwaway repo."""
        for key, value in (('root_dir', self.repo), ('private_key_file', self.secrets / 'id'),
                           ('enc_key_file', self.secrets / 'enc-key.json')):
            patcher = patch.dict(crypto_config, {key: value})
            patcher.start()
            self.addCleanup(patcher.stop)
        # `config` serves its settings out of a `_data` dict via __getattr__, so the entry is
        # what there is to patch — there is no attribute to shadow.
        patcher = patch.dict(import_module('solver.config').config._data, {'root_dir': self.repo})
        patcher.start()
        self.addCleanup(patcher.stop)
        # Both loaders are process-wide lru_caches, and each test mints its own keypair: left
        # warm, the second test unwraps its own enc-key file with the first test's private key
        # and reads the result as "HEAD does not decrypt". Clear entering and leaving.
        for cache in (load_private_key, read_master_key):
            cache.cache_clear()
            self.addCleanup(cache.cache_clear)

    def write_master_key(self, master_key: bytes) -> bytes:
        """Install *master_key* as the one this machine holds, invalidating the cache."""
        payload = enc_key_payload(self.private_key.public_key(), master_key)
        (self.secrets / 'enc-key.json').write_text(dumps(payload))
        read_master_key.cache_clear()
        load_private_key.cache_clear()
        return master_key

    def _git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(['git', *args], cwd=self.repo, env=self.env,
                                capture_output=True, text=True)
        if check:
            self.assertEqual(result.returncode, 0, f'git {" ".join(args)}: {result.stderr}')
        return result

    def _wire(self) -> None:
        base = f'{sys.executable} -P -m solver.crypto.gitfilter'
        for action in ('process', 'clean', 'smudge'):
            self._git('config', f'filter.solver-crypt.{action}', f'{base} {action}')
        self._git('config', 'filter.solver-crypt.required', 'true')

    def rotate(self) -> None:
        """Do to this repo what `key-rekey` does — then leave the clone behind the rotation.

        The published tree gets the new key and reaches origin; the clone's own HEAD is moved
        back to the pre-rotation commit without touching the worktree, because a hard reset
        would have to check out blobs it can no longer read. That is the live wedge, exactly.
        """
        before = self._git('rev-parse', 'HEAD').stdout.strip()
        # The rotation happens on the *operator's* tree, which never held this collaborator's
        # edits — so publish the pristine content and put the worktree back afterwards. Getting
        # this wrong makes the published blob already contain the edit, and a test that then
        # proves nothing about carrying it across.
        working = self.solution.read_bytes()
        self.solution.write_text(_PLAINTEXT)
        self.write_master_key(token_bytes(32))
        self._git('add', '--renormalize', '--', 'solutions/private')
        self._git('commit', '-qm', 'chore(crypto): re-encrypt under the rotated key')
        self._git('push', '-q', 'origin', 'master')
        # --mixed, not --soft: a stale clone's index matches its HEAD. Neither touches the
        # worktree, which is the point — checking out the old tree is the thing that cannot be
        # done any more.
        self._git('reset', '-q', '--mixed', before)
        self._git('update-ref', 'refs/remotes/origin/master', 'HEAD')  # a clone that never fetched
        self.solution.write_bytes(working)

    def test_head_is_readable_before_a_rotation_and_not_after(self) -> None:
        """The trigger itself: the check must fire on exactly one of the two states."""
        from solver.core import git
        self.assertTrue(git._head_private_opens(), 'own tree, own key — nothing to repair')
        self.rotate()
        self.assertFalse(git._head_private_opens(), 'HEAD predates the rotation: unreadable')

    def test_the_wedge_is_real_git_cannot_stash(self) -> None:
        """Proof that this is worth repairing: the ordinary sync path cannot run at all.

        `git-sync` stashes before merging, and the stash resets the worktree to HEAD. If this
        ever starts passing, the premise of the whole module has changed.
        """
        self.rotate()
        self.solution.write_text(_PLAINTEXT + '# local edit\n')
        result = self._git('stash', 'push', '-m', 'before merge', check=False)
        self.assertNotEqual(result.returncode, 0, 'a stash must fail on an unreadable HEAD')

    def test_saving_a_rotated_key_lands_the_clone_on_the_published_tree(self) -> None:
        """The repair: after it, HEAD is origin/master and the solution reads as plaintext."""
        from solver.core import git
        self.rotate()
        git.enc_key_arrived()
        self.assertEqual(self._git('rev-parse', 'HEAD').stdout.strip(),
                         self._git('rev-parse', 'origin/master').stdout.strip())
        self.assertEqual(self.solution.read_text(), _PLAINTEXT, 'decrypted in place')
        self.assertTrue(git._head_private_opens(), 'and readable from here on')

    def test_local_edits_collected_before_the_key_changed_survive(self) -> None:
        """Plaintext is key-agnostic, which is the only reason carrying edits across works.

        `msg save` reads them while the old key still answers, so they can be told apart from
        the rotation's own churn; the re-home writes them back over the published tree.
        """
        from solver.core import git
        self.solution.write_text(_PLAINTEXT + '# mine\n')
        edits = git.private_local_edits()          # as `save_issued_key` does: before the write
        self.assertEqual(list(edits), [_SOLUTION], 'exactly the edited file, no rotation churn')
        self.rotate()
        git.enc_key_arrived(edits)
        self.assertEqual(self.solution.read_text(), _PLAINTEXT + '# mine\n', 'edit kept')
        self.assertEqual(self._git('rev-parse', 'HEAD').stdout.strip(),
                         self._git('rev-parse', 'origin/master').stdout.strip())
        # And it reads as a normal local change again — the clean filter re-encrypts it under
        # the new key, so the diff is the edit rather than the rotation.
        self.assertEqual(self._git('diff', '--name-only').stdout.split(), [_SOLUTION])

    def test_unpushed_commits_are_never_orphaned(self) -> None:
        """Refusing is the correct answer when the alternative is discarding someone's work."""
        from solver.core import git
        self.rotate()
        (self.repo / 'notes.md').write_text('public work, not yet pushed\n')
        self._git('add', 'notes.md')
        self._git('commit', '-qm', 'work in progress')
        head = self._git('rev-parse', 'HEAD').stdout.strip()
        git.enc_key_arrived()
        self.assertEqual(self._git('rev-parse', 'HEAD').stdout.strip(), head, 'left untouched')
        self.assertTrue((self.repo / 'notes.md').exists())


if __name__ == '__main__':
    unittest.main()
