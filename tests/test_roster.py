#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The tracked roster (`users/users.json`) and the grant that writes it.

Two things are under test, and they are the two rules the file lives by:

- **it is a convenience, never an authority.** Every degraded state — absent, mangled, from a
  future version — must read as *empty*, because every caller's fallback is to ask the host,
  and a roster that raised would break commands that used to work without it;
- **it publishes no address.** Records are keyed by slug, in a public repository, and the one
  thing that must never leak in is the e-mail behind it.

Plus `user-authorize`, which is now the roster write and the split delivery in one act: it
records the public key, refuses when the repository's half is missing or stale, and dismisses
the request only once a half has actually gone out.

Everything runs against a temp roster (`$EULER_ROSTER_FILE`) and a temp secrets dir, so the
real users.json is never read or written.
"""
from __future__ import annotations

import json
import os
import unittest
from pathlib import Path
from secrets import token_bytes
from tempfile import TemporaryDirectory

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from solver.auth import roster
from solver.auth.identity import system_slug
from solver.crypto import keys as keys_mod
from solver.crypto.ciphers import enc_key_payload, load_private_key, public_key_hex, read_master_key
from solver.crypto.config import config as crypto_config
from solver.shell import dialogue
from tests import silence

silence()   # these drive the console's refusal paths on purpose

_THEM = 'them@example.com'


class RosterFileTestCase(unittest.TestCase):
    """A throwaway roster, pointed at by the env override the deployed tier also honours."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self._saved = os.environ.get(roster.ROSTER_FILE_ENV)
        os.environ[roster.ROSTER_FILE_ENV] = str(self.dir / 'users.json')
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        if self._saved is None:
            os.environ.pop(roster.ROSTER_FILE_ENV, None)
        else:
            os.environ[roster.ROSTER_FILE_ENV] = self._saved
        self._tmp.cleanup()


class StoreTests(RosterFileTestCase):
    """The reader is total: every bad state is an empty roster, never an exception."""

    def test_an_absent_roster_reads_empty(self) -> None:
        self.assertEqual(roster.read_roster()['users'], {})
        self.assertEqual(roster.public_keys(), {})
        self.assertEqual(roster.slugs(), [])

    def test_a_mangled_roster_reads_empty_rather_than_raising(self) -> None:
        """It is tracked, so it arrives through merges like any other file — conflict markers
        included. Every caller's fallback is to ask the host; raising would take that away."""
        for junk in ('{ not json', '<<<<<<< HEAD\n{}\n=======', '[]', 'null'):
            with self.subTest(junk=junk[:12]):
                roster.roster_path().write_text(junk)
                self.assertEqual(roster.read_roster()['users'], {})

    def test_a_roster_from_the_future_is_not_guessed_at(self) -> None:
        roster.roster_path().write_text(json.dumps({'version': roster.VERSION + 1,
                                                    'users': {'u123456': {'public_key': 'ab'}}}))
        self.assertEqual(roster.read_roster()['users'], {},
                         'a schema this reader does not know must not be half-read')

    def test_upsert_merges_rather_than_replaces(self) -> None:
        """Each act knows only its own field, and they arrive at different times."""
        roster.upsert(_THEM, scope='web', invited='2026-01-01T00:00:00+00:00')
        roster.upsert(_THEM, public_key='ab' * 32)
        entry = roster.user_entry(_THEM) or {}
        self.assertEqual(entry.get('scope'), 'web')
        self.assertEqual(entry.get('invited'), '2026-01-01T00:00:00+00:00')
        self.assertEqual(entry.get('public_key'), 'ab' * 32)

    def test_records_are_keyed_by_slug_and_carry_no_address(self) -> None:
        roster.upsert(_THEM, public_key='ab' * 32, scope='web')
        self.assertIn(system_slug(_THEM), roster.read_roster()['users'])
        self.assertNotIn(_THEM, roster.roster_path().read_text())

    def test_either_form_of_a_name_reaches_the_same_record(self) -> None:
        """The operator types an address; a command that already holds a box key passes the
        slug. Collapsing them here is what lets a roster key be a message recipient."""
        roster.upsert(_THEM, public_key='ab' * 32)
        self.assertEqual(roster.user_entry(system_slug(_THEM)), roster.user_entry(_THEM))

    def test_a_removed_record_is_kept_but_left_out_of_the_registry(self) -> None:
        """The note that they once had access is worth keeping; re-issuing to them is not."""
        roster.upsert(_THEM, public_key='ab' * 32, scope='web')
        roster.upsert(_THEM, removed=roster.stamp())
        self.assertIn(system_slug(_THEM), roster.read_roster()['users'])
        self.assertEqual(roster.public_keys(), {})
        self.assertEqual(roster.slugs(), [])

    def test_keys_without_a_value_are_not_a_registry_entry(self) -> None:
        roster.upsert(_THEM, public_key='', scope='web')
        self.assertEqual(roster.public_keys(), {})

    def test_no_key_material_is_ever_written_here(self) -> None:
        """The roster holds public keys and dates, and that is the whole of it. Half the master
        key used to live here too — safe mathematically, wrong in a public repository."""
        roster.upsert(_THEM, public_key='ab' * 32, scope='web', key_issued=roster.stamp())
        body = roster.roster_path().read_text()
        self.assertNotIn('share', body)
        self.assertNotIn('verify', body)
        self.assertEqual(set(roster.read_roster()), {'version', 'users'})


class AuthorizeTests(RosterFileTestCase):
    """`user-authorize`: record the key, then deliver half of one — or refuse before either."""

    def setUp(self) -> None:
        super().setUp()
        self._saved_crypto = {key: crypto_config[key]
                              for key in ('enc_key_file', 'private_key_file', 'share_file')}
        crypto_config['enc_key_file'] = self.dir / 'enc-key.json'
        crypto_config['private_key_file'] = self.dir / 'id'
        crypto_config['share_file'] = self.dir / 'share.json'
        self.addCleanup(self._restore_crypto)
        self.master = token_bytes(32)
        self.their_key = x25519.X25519PrivateKey.generate()
        self.theirs = public_key_hex(self.their_key.public_key())
        mine = x25519.X25519PrivateKey.generate()
        crypto_config['private_key_file'].write_bytes(
            mine.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
        load_private_key.cache_clear()
        keys_mod.write_enc_key_file(enc_key_payload(mine.public_key(), self.master))
        read_master_key.cache_clear()
        self.sent: list[tuple[str, str, str]] = []
        self.dismissed: list[str] = []
        import solver.web.msg.notify as notify_mod
        for module, name, stub in (
                (notify_mod, 'notify_user',
                 lambda identity, subject, body: bool(self.sent.append((identity, subject, body))
                                                      or True)),
                (notify_mod, 'dismiss_thread',
                 lambda thread_id: bool(self.dismissed.append(thread_id) or True)),
                (keys_mod, 'sure', lambda _q, *, phrase='': True)):
            saved = getattr(module, name)
            setattr(module, name, stub)
            self.addCleanup(setattr, module, name, saved)

    def _restore_crypto(self) -> None:
        for key, value in self._saved_crypto.items():
            crypto_config[key] = value
        load_private_key.cache_clear()
        read_master_key.cache_clear()

    def test_a_grant_records_the_key_and_sends_half_of_one(self) -> None:
        keys_mod.key_split(_THEM, self.theirs)                   # lay the repository's half
        self.assertEqual(keys_mod.user_authorize(self.theirs, _THEM), 0)
        self.assertEqual((roster.user_entry(_THEM) or {}).get('public_key'), self.theirs)
        self.assertEqual(len(self.sent), 1)
        share = keys_mod._unwrap_share(self.their_key,
                                       keys_mod.share_in_message(self.sent[-1][2]) or '')
        assert share is not None
        local = keys_mod.read_local_share() or {}
        self.assertEqual(keys_mod._reconstruct_secret([local['share'], share]), self.master)

    def test_a_grant_refuses_while_the_repository_has_no_half(self) -> None:
        """The failure `key-split` alone cannot catch: it would lay a fresh half, report
        success, and the request would be dismissed as worked with nothing delivered."""
        self.assertEqual(keys_mod.user_authorize(self.theirs, _THEM), 1)
        self.assertEqual(self.sent, [], 'nothing may be sent')
        self.assertEqual(self.dismissed, [], 'and the request stays in the queue')

    def test_a_grant_refuses_while_the_repositorys_half_predates_the_key(self) -> None:
        keys_mod.key_split(_THEM, self.theirs)
        keys_mod.write_enc_key_file(enc_key_payload(load_private_key().public_key(),
                                                    token_bytes(32)))     # rotated under it
        read_master_key.cache_clear()
        self.assertEqual(keys_mod.user_authorize(self.theirs, _THEM), 1)
        self.assertEqual(self.sent, [])

    def test_a_bare_key_still_needs_somebody_to_send_it_to(self) -> None:
        """A key on its own names nobody: there is no thread to take a requester from, and a
        half sent to nobody is a half in the spool with no reader."""
        keys_mod.key_split(_THEM, self.theirs)
        self.assertEqual(keys_mod.user_authorize(self.theirs), 1)
        self.assertEqual(self.sent, [])

    def test_a_target_that_is_neither_a_key_nor_a_message_id_is_refused(self) -> None:
        self.assertEqual(keys_mod.user_authorize('not-a-key', _THEM), 1)
        self.assertEqual(self.sent, [])


class HostGrantTests(RosterFileTestCase):
    """`host-authorize` / `host-unlock`: the off-host pair, where there is no shared half."""

    def setUp(self) -> None:
        super().setUp()
        self._saved_crypto = {key: crypto_config[key]
                              for key in ('enc_key_file', 'private_key_file', 'share_file')}
        crypto_config['enc_key_file'] = self.dir / 'enc-key.json'
        crypto_config['private_key_file'] = self.dir / 'id'
        crypto_config['share_file'] = self.dir / 'share.json'
        self.addCleanup(self._restore_crypto)
        self.master = token_bytes(32)
        self.mine = x25519.X25519PrivateKey.generate()
        crypto_config['private_key_file'].write_bytes(
            self.mine.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
        load_private_key.cache_clear()
        keys_mod.write_enc_key_file(enc_key_payload(self.mine.public_key(), self.master))
        read_master_key.cache_clear()
        self.mailed: list[tuple[str, str]] = []
        self._wired: list[str] = []
        import solver.core.git as git_mod
        import solver.web.auth.mail as mail_mod
        for module, name, stub in (
                (mail_mod.Mailer, 'send_master_key',
                 lambda _self, rcpt, block: self.mailed.append((rcpt, block))),
                (git_mod, 'enc_key_arrived', lambda edits=None: self._wired.append('wired')),
                (keys_mod, 'sure', lambda _q, *, phrase='': True)):
            saved = getattr(module, name)
            setattr(module, name, stub)
            self.addCleanup(setattr, module, name, saved)

    def _restore_crypto(self) -> None:
        for key, value in self._saved_crypto.items():
            crypto_config[key] = value
        load_private_key.cache_clear()
        read_master_key.cache_clear()

    def test_the_mailed_block_unlocks_the_machine_it_was_sealed_to(self) -> None:
        """The whole round trip: seal to a public key, mail it, paste it back."""
        self.assertEqual(keys_mod.host_authorize(public_key_hex(self.mine.public_key()),
                                                 'me@example.com'), 0)
        rcpt, block = self.mailed[-1]
        self.assertEqual(rcpt, 'me@example.com')
        self.assertIn(keys_mod._BLOCK_BEGIN, block)
        self.assertIn(keys_mod._BLOCK_END, block)

        crypto_config['enc_key_file'].unlink()                   # a machine holding nothing
        read_master_key.cache_clear()
        self.assertEqual(keys_mod.host_unlock(block), 0)
        read_master_key.cache_clear()
        self.assertEqual(read_master_key(), self.master)
        self.assertEqual(self._wired, ['wired'], 'gaining access must wire the filter')

    def test_the_block_survives_a_mail_client(self) -> None:
        """It crosses a mail client, so it arrives quoted, wrapped and surrounded by prose.
        The markers are for the person choosing what to copy; the braces are the contract."""
        keys_mod.host_authorize(public_key_hex(self.mine.public_key()), 'me@example.com')
        block = self.mailed[-1][1]
        crypto_config['enc_key_file'].unlink()
        read_master_key.cache_clear()
        self.assertEqual(keys_mod.host_unlock(f'Hi!\n\n{block}\n\n-- \nSent from my phone\n'), 0)

    def test_a_block_sealed_to_another_machine_is_refused(self) -> None:
        theirs = x25519.X25519PrivateKey.generate()
        keys_mod.host_authorize(public_key_hex(theirs.public_key()), 'them@example.com')
        block = self.mailed[-1][1]
        crypto_config['enc_key_file'].unlink()
        read_master_key.cache_clear()

        self.assertEqual(keys_mod.host_unlock(block), 1)
        self.assertFalse(crypto_config['enc_key_file'].exists(), 'nothing may be written')

    def test_nothing_is_mailed_for_a_key_that_is_not_one(self) -> None:
        self.assertEqual(keys_mod.host_authorize('not-a-public-key', 'me@example.com'), 1)
        self.assertEqual(self.mailed, [])

    def test_an_unreachable_relay_prints_the_block_rather_than_losing_it(self) -> None:
        """The payload is already sealed, so showing it costs nothing — and a relay that is
        down, absent or firewalled off must not turn into a grant that never happened."""
        import solver.web.auth.mail as mail_mod

        def refuse(_self: object, _rcpt: str, _block: str) -> None:
            raise OSError('connection refused')

        saved = mail_mod.Mailer.send_master_key
        mail_mod.Mailer.send_master_key = refuse                 # type: ignore[method-assign]
        self.addCleanup(setattr, mail_mod.Mailer, 'send_master_key', saved)
        self.assertEqual(keys_mod.host_authorize(public_key_hex(self.mine.public_key()),
                                                 'me@example.com'), 1)

    def test_both_ends_need_something_to_work_with(self) -> None:
        with self.assertRaises(dialogue.Abort):
            keys_mod.host_authorize('', 'me@example.com')
        with self.assertRaises(dialogue.Abort):
            keys_mod.host_unlock('')


if __name__ == '__main__':
    unittest.main()
