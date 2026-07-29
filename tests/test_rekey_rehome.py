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
        # An empty package marker, as every private problem directory carries. Git runs no
        # clean filter on empty content, so this is 0 bytes in the worktree and ciphertext in
        # the commit — the asymmetry that made a pristine clone report hundreds of edits.
        (self.solution.parent / '__init__.py').write_text('')
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

    def rotate_without_the_key(self) -> None:
        """Publish a rotation this clone was never issued: it keeps the key it has.

        The live state at login — the collaborator is coherent, holding a superseded key,
        and it is `origin/master` that no longer decrypts.
        """
        held = (self.secrets / 'enc-key.json').read_text()
        self.rotate()
        (self.secrets / 'enc-key.json').write_text(held)   # they never ran `msg save`
        read_master_key.cache_clear()
        load_private_key.cache_clear()
        self._git('fetch', '-q', 'origin', 'master')
        self._git('update-ref', 'refs/remotes/origin/master', 'FETCH_HEAD')

    def test_head_is_readable_before_a_rotation_and_not_after(self) -> None:
        """The trigger itself: the check must fire on exactly one of the two states."""
        from solver.core import git
        self.assertTrue(git.private_tree_opens(), 'own tree, own key — nothing to repair')
        self.rotate()
        self.assertFalse(git.private_tree_opens(), 'HEAD predates the rotation: unreadable')

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
        self.assertTrue(git.private_tree_opens(), 'and readable from here on')

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
        # the new key, so what is pending is the edit rather than the rotation. Asked through
        # `git status`, for the reason the empty-file test above records.
        self.assertEqual(self._git('status', '--porcelain').stdout.split(), ['M', _SOLUTION])

    def test_a_clone_holding_an_old_key_is_told_to_check_its_messages(self) -> None:
        """The login hint, from the side the live shells were actually on.

        At login the clone still held the *old* key and its *old* HEAD — which match, so
        asking only about HEAD says "all fine" and the hint fell through to "run `git-sync`
        to see why". The unreadable tree is the published one. Both sides now answer.
        """
        from solver.core import git
        self.assertEqual(git.key_waiting_hint(), '', 'in step: nothing to say')
        self.rotate_without_the_key()
        self.assertTrue(git.private_tree_opens('HEAD'), 'own history, own key: still readable')
        self.assertFalse(git.private_tree_opens('origin/master'), 'the published tree is not')
        # Named where the reader is looking: the header's message chip over the web, whose key
        # row has its own save button, and the shell verbs in a terminal, which has no header.
        app_config = import_module('solver.config').config
        for channel, expected in (('web', 'header'), ('terminal', 'msg save')):
            subject = app_config.subject._replace(channel=channel)
            with patch.dict(app_config._data, {'subject': subject}):
                self.assertIn(expected, git.key_waiting_hint(), f'{channel}: names its own way')

    def test_a_sync_refuses_rather_than_merging_what_it_cannot_read(self) -> None:
        """Merging anyway left a live clone with a filter traceback and a deleted file.

        The assertion is that `sync.sh` is never reached — a non-zero return alone proves
        nothing here, since the script would fail in this fixture regardless.
        """
        from solver.core import git
        self.rotate_without_the_key()
        commands: list[str] = []
        real = git.run_cmdline

        def recording(cmdline: str) -> int:
            commands.append(cmdline)
            return real(cmdline)

        git.run_cmdline = recording                      # type: ignore[assignment]
        self.addCleanup(setattr, git, 'run_cmdline', real)
        before = self._git('rev-parse', 'HEAD').stdout.strip()
        self.assertNotEqual(git.git_sync(), 0, 'a refusal, and a non-zero one')
        self.assertEqual([c for c in commands if 'sync' in c], [], 'the merge was never started')
        self.assertEqual(self._git('rev-parse', 'HEAD').stdout.strip(), before, 'nothing moved')
        self.assertEqual(self._git('status', '--porcelain').stdout, '', 'nothing half-applied')

    def test_an_untouched_worktree_reports_nothing(self) -> None:
        """The 917 bug proper: empty files are not edits.

        `git diff HEAD` says otherwise and always will — it compares the worktree's 0 bytes
        against the commit's ciphertext — which is why the question has to be `git status`.
        Two collaborators were told their pristine clones held 917 local edits.
        """
        from solver.core import git
        self.assertEqual(git.private_local_edits(), {}, 'nothing was edited')
        marker = self.solution.parent / '__init__.py'
        self.assertEqual(marker.stat().st_size, 0, 'the fixture must really be empty')
        self.assertGreater(self._git('cat-file', '-s', 'HEAD:' + _SOLUTION.rsplit('/', 1)[0]
                                     + '/__init__.py').stdout.strip(), '0', 'and encrypted')

    def test_an_unfiltered_file_does_not_mask_an_unreadable_tree(self) -> None:
        """A plaintext file sorting first under solutions/private must not answer for the tree.

        The check samples blobs, and sampling one is sampling the wrong one as soon as
        something lands under the tree that the attributes do not match. Answering "readable"
        from that would disable the repair silently.
        """
        from solver.core import git
        plain = self.repo / 'solutions/private/README.md'   # sorts before p0100_0199/
        plain.write_text('not a solution, not filtered\n')
        # Genuinely exempt, or the `**` rule would encrypt it and the test would pass for the
        # wrong reason — the whole point is a blob the filter never touched.
        (self.repo / '.gitattributes').write_text(
            'solutions/private/** filter=solver-crypt -text -diff\n'
            'solutions/private/README.md !filter\n')
        self._git('add', '-A')
        self._git('commit', '-qm', 'a plaintext file under the private tree')
        self._git('push', '-q', 'origin', 'master')
        self.rotate()
        self.assertFalse(git.private_tree_opens(), 'the encrypted blobs still decide')

    def test_a_wedged_clone_reports_no_edits_at_all(self) -> None:
        """The 917 bug: a clone already behind a rotation must not invent local edits.

        Reported live — `msg save` on a clone that had never re-homed from the *previous*
        rotation announced "kept your 917 local edit(s)" on a worktree with none. With the
        held key not matching HEAD, git cleans every present private file to a different blob
        than HEAD's and reports it as changed; writing those back would have pinned stale
        content over the published tree.
        """
        from solver.core import git
        self.rotate()                                    # HEAD no longer opens: already wedged
        self.assertEqual(git.private_local_edits(), {}, 'no readable HEAD, no answer')
        git.enc_key_arrived(git.private_local_edits())
        self.assertEqual(self.solution.read_text(), _PLAINTEXT, 'the published content, intact')
        self.assertEqual(self._git('status', '--porcelain').stdout, '', 'and a clean tree')

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
