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
import unittest
from pathlib import Path
from secrets import token_bytes
from tempfile import TemporaryDirectory

from cryptography.hazmat.primitives.asymmetric import x25519

from solver.auth.identity import system_slug
from solver.crypto import keys as keys_mod
from solver.crypto.ciphers import (authorised_keys, encrypt_blob, key_owners, lock, public_key_hex,
                                   read_enc_key_file, read_master_key)
from solver.crypto.config import config as crypto_config
from solver.web.auth import commands as users_mod
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
        self._with_thread(self._thread(f'{keys_mod._KEY_REQUEST_SUBJECT}them@example.com',
                                       f'minted a key\n\npublic key: {self.theirs}\n'))
        self.assertEqual(keys_mod._resolve_key_request('0123456789abcdef'),
                         (self.theirs, 'them@example.com'))

    def test_a_message_that_is_not_a_key_request_is_refused(self) -> None:
        """An arbitrary `msg send` must never be mined for hex."""
        self._with_thread(self._thread('Can you look at problem 42?', f'here it is {self.theirs}'))
        self.assertIsNone(keys_mod._resolve_key_request('0123456789abcdef'))

    def test_two_keys_in_the_body_are_refused(self) -> None:
        """Ambiguity is not resolved by picking one — a grant is not inferred."""
        self._with_thread(self._thread(f'{keys_mod._KEY_REQUEST_SUBJECT}them@example.com',
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
        self.assertTrue(subject.startswith(keys_mod._KEY_REQUEST_SUBJECT))
        self.assertEqual(len(keys_mod._PUBLIC_KEY_RE.findall(body)), 1)


if __name__ == '__main__':
    unittest.main()
