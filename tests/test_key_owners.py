#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Key attribution and purge: the ``owners`` entry of ``keys/enc-key.json``.

Covers the three things the feature rests on:

- the **file shape** is additive — `authorised_keys` / `key_owners` read a file with the
  new entry *and* one written before it existed, and a reader that only knows `verify`
  still unwraps its key. That is what keeps a collaborator on an older solver decrypting
  after the first attributed grant lands;
- **attribution is written by one command** — `user-authorize` — and carried or pruned by
  the two that rewrite the file wholesale (`key-rekey`, `revoke_keys`);
- **purge classification**, including the two guards that matter: the operator's own key
  is never a candidate, and a local os-login (whose roster row carries no slug) classifies
  by its computed slug rather than by that empty column.

Everything runs against a temp `keys/enc-key.json` with the crypto config rebound onto it,
so no real key material is read or written.
"""
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from secrets import token_bytes
from tempfile import TemporaryDirectory

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from solver.auth.identity import system_slug
from solver.auth.subject import Subject
from solver.config import config as app_config
from solver.core import git
from solver.crypto import keys as keys_mod
from solver.crypto.ciphers import (authorised_keys, encrypt_blob, key_owners, load_private_key, lock,
                                   prune_local_enc_key, public_key_hex, read_enc_key_file,
                                   read_local_enc_key, read_master_key, write_local_enc_key)
from solver.crypto.config import config as crypto_config
from solver.web.auth import commands as users_mod
from solver.web.msg import KEY_REQUEST_SUBJECT
from tests import silence

silence()   # the purge/authorize paths print refusals on purpose


def _keypair() -> tuple[x25519.X25519PrivateKey, str]:
    """A fresh X25519 pair and its public key hex (an entry's identity in the file)."""
    private = x25519.X25519PrivateKey.generate()
    return private, public_key_hex(private.public_key())


class EncKeyFileTestCase(unittest.TestCase):
    """Base: a temp enc-key.json holding a known master key wrapped to a set of pairs."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.enc_file = Path(self._tmp.name) / 'enc-key.json'
        self._saved = crypto_config['enc_key_file']
        crypto_config['enc_key_file'] = self.enc_file
        self.addCleanup(self._restore)
        self.master = token_bytes(32)
        self.mine_key, self.mine = _keypair()
        self.theirs_key, self.theirs = _keypair()
        self.gone_key, self.gone = _keypair()

    def _restore(self) -> None:
        crypto_config['enc_key_file'] = self._saved
        self._tmp.cleanup()
        read_master_key.cache_clear()

    def write(self, *, owners: dict[str, dict[str, str]] | None = None,
              public_keys: tuple[str, ...] = ()) -> None:
        """Write an enc-key.json wrapping the master key to *public_keys* (+ optional owners)."""
        data: dict[str, object] = {
            pub: lock(x25519.X25519PublicKey.from_public_bytes(bytes.fromhex(pub)), self.master)
            for pub in (public_keys or (self.mine, self.theirs, self.gone))}
        data['verify'] = encrypt_blob(crypto_config['verify_text'], self.master).hex()
        if owners is not None:
            data['owners'] = owners
        self.enc_file.write_text(json.dumps(data, indent=2))
        read_master_key.cache_clear()


class FileShapeTests(EncKeyFileTestCase):
    """`owners` is a sibling entry: additive, and invisible to everything but purge."""

    def test_authorised_keys_excludes_both_reserved_entries(self) -> None:
        self.write(owners={self.mine: {'slug': 'ua1b2c3', 'since': 'now', 'by': 'ua1b2c3'}})
        found = authorised_keys(read_enc_key_file())
        self.assertCountEqual(found, [self.mine, self.theirs, self.gone])
        self.assertNotIn('owners', found)
        self.assertNotIn('verify', found)

    def test_a_file_written_before_owners_existed_reads_clean(self) -> None:
        """The migration case: every key in the file today has no attribution."""
        self.write()
        data = read_enc_key_file()
        self.assertEqual(key_owners(data), {})
        self.assertEqual(len(authorised_keys(data)), 3)

    def test_an_older_reader_still_unwraps_with_owners_present(self) -> None:
        """The compatibility promise: `owners` must not disturb the decrypt path.

        `read_master_key` indexes by public key and takes `verify` by name — exactly what a
        clone running an older solver does — so a file carrying attribution unwraps there too.
        """
        self.write(owners={self.mine: {'slug': 'ua1b2c3', 'since': 'now', 'by': 'ua1b2c3'}})
        data = read_enc_key_file()
        from solver.crypto.ciphers import unlock
        self.assertEqual(unlock(self.mine_key, data[self.mine]), self.master)

    def test_key_owners_ignores_a_malformed_entry(self) -> None:
        self.write()
        data = read_enc_key_file()
        data['owners'] = {self.mine: 'not-a-record'}
        self.assertEqual(key_owners(data), {})


class RewriteTests(EncKeyFileTestCase):
    """The two commands that rewrite the file wholesale keep attribution honest."""

    def test_rekey_carries_owners_forward_pruned_to_survivors(self) -> None:
        owners = {self.mine: {'slug': 'umine', 'since': 'now', 'by': 'umine'},
                  self.gone: {'slug': 'ugone', 'since': 'now', 'by': 'umine'}}
        body = keys_mod._wrapped_for_all(token_bytes(32), [self.mine, self.theirs], owners)
        self.assertEqual(set(key_owners(body)), {self.mine})     # the dropped key's record goes with it

    def test_revoke_drops_the_key_and_its_owner(self) -> None:
        self.write(owners={self.gone: {'slug': 'ugone', 'since': 'now', 'by': 'umine'}})
        self.assertEqual(keys_mod.revoke_keys([self.gone]), 1)
        data = read_enc_key_file()
        self.assertNotIn(self.gone, authorised_keys(data))
        self.assertEqual(key_owners(data), {})
        self.assertIn('verify', data)                            # the file is still usable

    def test_revoke_refuses_to_empty_the_file(self) -> None:
        """A file with no keys in it is unreadable and unrecoverable — never reachable by typo."""
        self.write()
        self.assertEqual(keys_mod.revoke_keys([self.mine, self.theirs, self.gone]), 0)
        self.assertEqual(len(authorised_keys(read_enc_key_file())), 3)

    def test_revoke_of_an_absent_key_changes_nothing(self) -> None:
        self.write()
        _, absent = _keypair()
        self.assertEqual(keys_mod.revoke_keys([absent]), 0)
        self.assertEqual(len(authorised_keys(read_enc_key_file())), 3)


class ClassificationTests(EncKeyFileTestCase):
    """`users purge`'s decision: which entry still belongs to somebody."""

    def test_the_four_classes(self) -> None:
        self.write(owners={
            self.theirs: {'slug': system_slug('them@example.com'), 'since': 'now', 'by': 'umine'},
            self.gone: {'slug': system_slug('left@example.com'), 'since': 'now', 'by': 'umine'}})
        roster = [{'user': 'them@example.com', 'profile': 'contributor', 'scope': 'web',
                   'state': 'registered', 'slug': system_slug('them@example.com')}]
        found = {key: klass for key, klass, _note in users_mod._classify_keys(roster, self.mine)}
        self.assertEqual(found[self.mine], 'self')            # the running operator's own key
        self.assertEqual(found[self.theirs], 'active')        # owner is on the roster
        self.assertEqual(found[self.gone], 'stale')           # owner is not
        _, orphan = _keypair()
        self.write(public_keys=(self.mine, orphan))
        rows = users_mod._classify_keys(roster, self.mine)
        self.assertEqual(dict((k, c) for k, c, _ in rows)[orphan], 'unattributed')

    def test_a_disabled_account_is_stale(self) -> None:
        self.write(owners={self.theirs: {'slug': system_slug('them@example.com'),
                                         'since': 'now', 'by': 'umine'}})
        roster = [{'user': 'them@example.com', 'profile': 'reader', 'scope': 'web',
                   'state': 'disabled', 'slug': system_slug('them@example.com')}]
        found = {key: klass for key, klass, _note in users_mod._classify_keys(roster, self.mine)}
        self.assertEqual(found[self.theirs], 'stale')

    def test_a_local_os_login_classifies_by_computed_slug(self) -> None:
        """The roster's own `slug` column is empty for a local login — the operator's usual shape.

        Reading that column instead of computing the slug would classify the operator's
        colleague-on-an-os-login as belonging to nobody, and offer their key for purge.
        """
        self.write(owners={self.theirs: {'slug': system_slug('vikas'), 'since': 'now', 'by': 'umine'}})
        roster = [{'user': 'vikas', 'profile': 'admin', 'scope': 'local',
                   'state': 'os-login', 'slug': ''}]
        found = {key: klass for key, klass, _note in users_mod._classify_keys(roster, self.mine)}
        self.assertEqual(found[self.theirs], 'active')

    def test_self_sorts_first_and_stale_last(self) -> None:
        """Print order is the reading order: what you must not touch, then what is on offer."""
        self.write(owners={self.gone: {'slug': system_slug('left@example.com'),
                                       'since': 'now', 'by': 'umine'}})
        rows = users_mod._classify_keys([], self.mine)
        self.assertEqual(rows[0][1], 'self')
        self.assertEqual(rows[-1][1], 'stale')


class LocalOverlayTests(EncKeyFileTestCase):
    """The machine-local stopgap: `~/.euler/enc-key.local.json`.

    It exists because the carry used to be written into the **tracked** file, which put
    per-machine state into shared state: `sync.sh` stashes a dirty tree around the merge
    and pops it after, so when the maintainer's authorised copy of that same file arrived
    the pop conflicted — and the conflict markers left the JSON unparseable, which reads as
    "not authorised" everywhere and takes decryption down with it. A reader could not even
    recover (`git-reset` is contributor-floored).

    The rules, in the order the read path applies them: tracked wins and the overlay is
    deleted; otherwise the overlay serves; otherwise no access.
    """

    def setUp(self) -> None:
        super().setUp()
        self._saved_local = crypto_config['enc_key_local_file']
        crypto_config['enc_key_local_file'] = self.enc_file.parent / 'enc-key.local.json'
        self.addCleanup(lambda: crypto_config.__setitem__('enc_key_local_file', self._saved_local))
        crypto_config['private_key_file'] = self.enc_file.parent / 'id'
        self.addCleanup(load_private_key.cache_clear)

    def _be(self, private: x25519.X25519PrivateKey) -> None:
        """Become the holder of *private* — the identity `read_master_key` resolves."""
        crypto_config['private_key_file'].write_bytes(private.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
        load_private_key.cache_clear()
        read_master_key.cache_clear()

    def test_the_overlay_grants_access_when_the_tracked_file_does_not(self) -> None:
        """The whole point: rotate, and keep decrypting until the grant lands."""
        self.write(public_keys=(self.theirs,))               # the shared file does NOT name us
        self._be(self.mine_key)
        with self.assertRaises(KeyError):
            read_master_key()
        write_local_enc_key(self.mine, lock(self.mine_key.public_key(), self.master))
        read_master_key.cache_clear()
        self.assertEqual(read_master_key(), self.master)

    def test_the_tracked_file_wins_but_the_read_does_not_delete_the_overlay(self) -> None:
        """A read must not retire the fallback — mid-merge the tracked file is transient.

        git writes the incoming keys/enc-key.json while it checks out solutions/private, so
        the filter sees a file naming this key; if the merge then fails and `sync.sh` rolls
        it back, a read that had deleted the overlay leaves the user with no access at all.
        That is how this was found, on a reader whose sync had already rolled back once.
        """
        self.write(public_keys=(self.mine,))
        write_local_enc_key(self.mine, lock(self.mine_key.public_key(), self.master))
        self._be(self.mine_key)
        self.assertEqual(read_master_key(), self.master)
        self.assertIn(self.mine, read_local_enc_key(), 'the fallback must survive the read')

    def test_a_rolled_back_merge_leaves_access_intact(self) -> None:
        """The whole scenario, end to end: see the new file, lose it again, still decrypt."""
        write_local_enc_key(self.mine, lock(self.mine_key.public_key(), self.master))
        self._be(self.mine_key)
        self.write(public_keys=(self.mine,))                 # mid-merge: the new file is on disk
        self.assertEqual(read_master_key(), self.master)
        self.write(public_keys=(self.theirs,))               # …the merge rolls back
        read_master_key.cache_clear()
        self.assertEqual(read_master_key(), self.master, 'the overlay must still carry them')

    def test_pruning_retires_the_overlay_once_the_tracked_file_names_the_key(self) -> None:
        """From a settled tree — `user`, or a completed git-sync — the stopgap goes."""
        self.write(public_keys=(self.mine,))
        write_local_enc_key(self.mine, lock(self.mine_key.public_key(), self.master))
        self._be(self.mine_key)
        prune_local_enc_key()
        self.assertEqual(read_local_enc_key(), {})
        self.assertFalse(crypto_config['enc_key_local_file'].exists())

    def test_pruning_keeps_an_overlay_the_tracked_file_has_not_superseded(self) -> None:
        self.write(public_keys=(self.theirs,))
        write_local_enc_key(self.mine, lock(self.mine_key.public_key(), self.master))
        self._be(self.mine_key)
        prune_local_enc_key()
        self.assertIn(self.mine, read_local_enc_key())

    def test_a_stale_overlay_for_a_rotated_away_key_is_ignored(self) -> None:
        """Keyed by public key, so an overlay written for a key we no longer hold cannot serve."""
        self.write(public_keys=(self.theirs,))
        write_local_enc_key(self.gone, lock(self.gone_key.public_key(), self.master))
        self._be(self.mine_key)
        with self.assertRaises(KeyError):
            read_master_key()

    def test_a_second_rotation_supersedes_the_first(self) -> None:
        """One entry, always the latest — a stopgap must not accumulate keys nobody purges."""
        write_local_enc_key(self.mine, 'aa')
        write_local_enc_key(self.theirs, 'bb')
        self.assertEqual(read_local_enc_key(), {self.theirs: 'bb'})

    def test_a_malformed_overlay_reads_as_absent(self) -> None:
        """A broken stopgap degrades to "no access yet", never to an exception on the
        filter's path — the failure this whole design exists to prevent."""
        self.write(public_keys=(self.theirs,))
        crypto_config['enc_key_local_file'].write_text('<<<<<<< HEAD not json')
        self._be(self.mine_key)
        self.assertEqual(read_local_enc_key(), {})
        with self.assertRaises(KeyError):
            read_master_key()

    def test_the_overlay_is_still_held_to_the_verify_check(self) -> None:
        """Reaching the key by the side door does not lower the bar it must clear."""
        self.write(public_keys=(self.theirs,))
        write_local_enc_key(self.mine, lock(self.mine_key.public_key(), token_bytes(32)))
        self._be(self.mine_key)
        with self.assertRaises(ValueError):
            read_master_key()

    def test_regen_writes_the_overlay_and_never_the_tracked_file(self) -> None:
        """The regression: a rotation must leave keys/enc-key.json byte-identical."""
        import solver.crypto.keys as mod
        self.write(public_keys=(self.mine,))
        before = self.enc_file.read_text()
        self._be(self.mine_key)
        saved_confirm, mod.confirm = mod.confirm, lambda _p: True
        self.addCleanup(setattr, mod, 'confirm', saved_confirm)
        saved_follow = mod._make_the_rotation_durable
        mod._make_the_rotation_durable = lambda _s, _p: None     # type: ignore[assignment]
        self.addCleanup(setattr, mod, '_make_the_rotation_durable', saved_follow)
        saved_emit, mod.osc.emit = mod.osc.emit, lambda *a, **k: None
        self.addCleanup(setattr, mod.osc, 'emit', saved_emit)
        saved_subject = app_config.subject
        app_config.subject = Subject(user='t@example.com', slug='t-000000', channel='web',
                                     auth_method='test', profile='contributor')
        self.addCleanup(setattr, app_config, 'subject', saved_subject)

        self.assertEqual(mod.user(regen=True), 0)
        self.assertEqual(self.enc_file.read_text(), before, 'the tracked file must not be touched')
        self.assertEqual(len(read_local_enc_key()), 1, 'the carry went to the overlay')
        self.assertEqual(read_master_key(), self.master, 'and access survived the rotation')


class SyncHealTests(unittest.TestCase):
    """`git-sync`'s one-time repair of a locally-modified keys/enc-key.json.

    Runs against a real throwaway git repo, because the repair is a `git checkout HEAD --`
    — a destructive operation on a file that carries master-key access, and the one test
    worth having is that it cannot destroy the access.
    """

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        for argv in (['git', 'init', '-q', '-b', 'master'],
                     ['git', 'config', 'user.email', 't@example.com'],
                     ['git', 'config', 'user.name', 'T']):
            subprocess.run(argv, cwd=self.repo, check=True, capture_output=True)
        (self.repo / 'keys').mkdir()
        self.master = token_bytes(32)
        self.mine_key, self.mine = _keypair()
        self.tracked = self.repo / 'keys' / 'enc-key.json'
        self.committed = {'verify': encrypt_blob(crypto_config['verify_text'], self.master).hex()}
        self.tracked.write_text(json.dumps(self.committed))
        subprocess.run(['git', 'add', '-A'], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-qm', 'init'], cwd=self.repo, check=True, capture_output=True)

        self._saved_root, app_config.root_dir = app_config.root_dir, self.repo
        self.addCleanup(setattr, app_config, 'root_dir', self._saved_root)
        self._saved_enc = crypto_config['enc_key_file']
        crypto_config['enc_key_file'] = self.tracked
        self._saved_local = crypto_config['enc_key_local_file']
        crypto_config['enc_key_local_file'] = self.repo / '.secrets' / 'enc-key.local.json'
        self._saved_id = crypto_config['private_key_file']
        crypto_config['private_key_file'] = self.repo / '.secrets' / 'id'
        crypto_config['private_key_file'].parent.mkdir()
        crypto_config['private_key_file'].write_bytes(self.mine_key.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
        self.addCleanup(self._restore_config)
        self._saved_subject = app_config.subject
        self.addCleanup(setattr, app_config, 'subject', self._saved_subject)
        load_private_key.cache_clear()
        read_master_key.cache_clear()

    def _restore_config(self) -> None:
        crypto_config['enc_key_file'] = self._saved_enc
        crypto_config['enc_key_local_file'] = self._saved_local
        crypto_config['private_key_file'] = self._saved_id
        load_private_key.cache_clear()
        read_master_key.cache_clear()

    def _be(self, profile: str) -> None:
        app_config.subject = Subject(user='t@example.com', slug='t-000000', channel='web',
                                     auth_method='test', profile=profile)

    def _dirty_with_my_key(self) -> None:
        """The state the old rotation left behind: our key added to the tracked file."""
        self.tracked.write_text(json.dumps(
            {**self.committed, self.mine: lock(self.mine_key.public_key(), self.master)}))

    def test_a_clean_tree_is_untouched(self) -> None:
        self._be('reader')
        git._heal_local_enc_key()
        self.assertEqual(json.loads(self.tracked.read_text()), self.committed)

    def test_a_readers_local_edit_is_restored_and_their_access_carried(self) -> None:
        """The repair must not cost them the very thing the edit was protecting."""
        self._be('reader')
        self._dirty_with_my_key()
        git._heal_local_enc_key()
        self.assertEqual(json.loads(self.tracked.read_text()), self.committed)   # restored…
        self.assertIn(self.mine, read_local_enc_key())                           # …access carried…
        self.assertEqual(read_master_key(), self.master)                         # …and still works

    def test_a_conflicted_file_is_restored_even_though_nothing_can_be_lifted(self) -> None:
        """The exact state a failed `git stash pop` leaves: markers, so no JSON to read.

        Restoring is still strictly better than the markers, which no reader can parse.
        """
        self._be('reader')
        self.tracked.write_text('<<<<<<< Updated upstream\n{}\n=======\n{}\n>>>>>>> Stashed changes\n')
        git._heal_local_enc_key()
        self.assertEqual(json.loads(self.tracked.read_text()), self.committed)

    def test_a_maintainers_edit_is_left_alone(self) -> None:
        """At that floor a modified enc-key.json is an authorization awaiting git-publish."""
        self._be('maintainer')
        self._dirty_with_my_key()
        git._heal_local_enc_key()
        self.assertIn(self.mine, json.loads(self.tracked.read_text()))


class RotationFollowThroughTests(EncKeyFileTestCase):
    """A minted key needs the same follow-through whether or not it currently decrypts.

    The regression these pin: `user --regen` carries master-key access to the new key **in
    the working tree only**, so `read_master_key()` succeeds afterwards — and the request
    was filed only from the failure branch. A collaborator rotated, saw a green tick, and
    silently lost access at their next `git-sync`, with nobody ever asked to authorise the
    new key.
    """

    def _capture(self) -> list[tuple[str, str]]:
        """Record what would be filed with staff instead of dialling the spool."""
        import solver.web.msg.notify as notify
        sent: list[tuple[str, str]] = []
        saved = notify.notify_staff
        notify.notify_staff = lambda subject, body: (sent.append((subject, body)), True)[1]  # type: ignore
        self.addCleanup(setattr, notify, 'notify_staff', saved)
        return sent

    @staticmethod
    def _subject(profile: str) -> Subject:
        return Subject(user='t@example.com', slug='t-000000', channel='web',
                       auth_method='test', profile=profile)

    def test_a_contributor_rotation_files_a_request(self) -> None:
        """They cannot authorise their own key, so somebody has to be told."""
        sent = self._capture()
        keys_mod._make_the_rotation_durable(self._subject('contributor'), self.theirs)
        self.assertEqual(len(sent), 1)
        subject, body = sent[0]
        self.assertTrue(subject.startswith(KEY_REQUEST_SUBJECT))
        self.assertIn('OLD key', body)                       # worded as a rotation…
        self.assertIn('users purge', body)                   # …whose old entry now wants purging
        self.assertEqual(len(keys_mod._PUBLIC_KEY_RE.findall(body)), 1)   # still machine-workable

    def test_a_maintainer_rotation_is_told_to_do_it_themselves(self) -> None:
        """Filing a request with staff when you *are* staff is filing it with yourself."""
        sent = self._capture()
        keys_mod._make_the_rotation_durable(self._subject('maintainer'), self.theirs)
        self.assertEqual(sent, [])

    def test_a_reader_rotation_files_a_request(self) -> None:
        sent = self._capture()
        keys_mod._make_the_rotation_durable(self._subject('reader'), self.theirs)
        self.assertEqual(len(sent), 1)

    def test_regen_reaches_the_follow_through_even_though_it_still_decrypts(self) -> None:
        """The branch itself — where the bug was.

        Drives the real `user --regen` against a temp identity that *is* authorised, so the
        carry succeeds and `read_master_key()` returns: the success path must still call the
        follow-through. Testing only the helper would have left this exact regression open.
        """
        import solver.crypto.keys as mod
        from solver.utils import shell_utils
        self.write(public_keys=(self.mine,))                 # our identity is the authorised one
        crypto_config['private_key_file'] = self.enc_file.parent / 'id'
        crypto_config['private_key_file'].write_bytes(self.mine_key.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
        mod.load_private_key.cache_clear()
        called: list[str] = []
        for name, stub in (('confirm', lambda _p: True),
                           ('_make_the_rotation_durable', lambda _s, pub: called.append(pub))):
            saved = getattr(mod, name)
            setattr(mod, name, stub)
            self.addCleanup(setattr, mod, name, saved)
        saved_confirm = shell_utils.confirm
        self.addCleanup(setattr, shell_utils, 'confirm', saved_confirm)
        saved_emit, mod.osc.emit = mod.osc.emit, lambda *a, **k: None
        self.addCleanup(setattr, mod.osc, 'emit', saved_emit)
        saved_subject = app_config.subject
        app_config.subject = self._subject('contributor')
        self.addCleanup(setattr, app_config, 'subject', saved_subject)

        self.assertEqual(mod.user(regen=True), 0)
        self.assertEqual(len(called), 1, 'the rotation follow-through must run on the success path')
        mod.load_private_key.cache_clear()


class KeyRequestTests(EncKeyFileTestCase):
    """`user-authorize <msg-id>` reads a key request — or refuses, rather than guessing."""

    def _thread(self, subject: str, body: str) -> dict[str, str]:
        return {'id': '0123456789abcdef', 'subject': subject, 'body': body,
                'author': 'box', 'author_name': 'them@example.com'}

    def _with_thread(self, thread: dict[str, str] | None) -> None:
        """Stub the spool read — these tests are about the parse, not the transport."""
        import solver.web.msg.notify as notify
        saved = notify.read_thread
        notify.read_thread = lambda _id: thread          # type: ignore[assignment]
        self.addCleanup(setattr, notify, 'read_thread', saved)

    def test_a_well_formed_request_yields_the_key_and_its_author(self) -> None:
        self._with_thread(self._thread(f'{KEY_REQUEST_SUBJECT}them@example.com',
                                       f'minted a key\n\npublic key: {self.theirs}\n'))
        self.assertEqual(keys_mod._resolve_key_request('0123456789abcdef'),
                         (self.theirs, 'them@example.com'))

    def test_a_message_that_is_not_a_key_request_is_refused(self) -> None:
        """An arbitrary `msg send` must never be mined for hex."""
        self._with_thread(self._thread('Can you look at problem 42?', f'here it is {self.theirs}'))
        self.assertIsNone(keys_mod._resolve_key_request('0123456789abcdef'))

    def test_two_keys_in_the_body_are_refused(self) -> None:
        """Ambiguity is not resolved by picking one — a grant is not inferred."""
        self._with_thread(self._thread(f'{KEY_REQUEST_SUBJECT}them@example.com',
                                       f'{self.theirs} and also {self.gone}'))
        self.assertIsNone(keys_mod._resolve_key_request('0123456789abcdef'))

    def test_an_unreachable_thread_is_refused(self) -> None:
        self._with_thread(None)
        self.assertIsNone(keys_mod._resolve_key_request('0123456789abcdef'))

    def test_the_request_notification_stays_machine_workable(self) -> None:
        """The subject/body contract `_resolve_key_request` depends on, asserted at the source.

        `_request_authorization` composes the message; if its wording drifts from the marker
        or grows a second hex token, every future `user-authorize <msg-id>` silently refuses.
        """
        import solver.web.msg.notify as notify
        sent: list[tuple[str, str]] = []
        saved = notify.notify_staff
        notify.notify_staff = lambda subject, body: (sent.append((subject, body)), True)[1]  # type: ignore
        self.addCleanup(setattr, notify, 'notify_staff', saved)
        keys_mod._request_authorization('them@example.com', self.theirs)
        subject, body = sent[0]
        self.assertTrue(subject.startswith(KEY_REQUEST_SUBJECT))
        self.assertEqual(len(keys_mod._PUBLIC_KEY_RE.findall(body)), 1)


if __name__ == '__main__':
    unittest.main()
