#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The machine-local enc-key file: two records, one holder, no shared state.

`~/.euler/enc-key.json` holds `verify` and the master key wrapped to *this machine's*
public key, and nothing else. It replaced a tracked, multi-entry `keys/enc-key.json` that
every collaborator committed and pulled — which is where a long run of failures came from:
a rotation dirtied a tracked file, `sync.sh` stashed and popped it around the merge, the pop
conflicted with the authorised copy arriving from the other side, and the conflict markers
left the JSON unparseable, which every reader takes for "not authorised". It also needed an
attribution map, a purge verb, a machine-local overlay and a repair path in `git-sync`, all
to answer questions a one-holder file does not raise.

What is left to test is small, which is the point:

- the read path — one entry, held to `verify`;
- issuance — a payload is the whole of somebody's file, wrapped to their key alone;
- taking an issued key (`msg act`) — it must **prove** a payload before overwriting the file that may be the only
  thing between this machine and the private tree;
- `user --regen` — carry the master key when it can be loaded, ask for it when it cannot,
  and never ask merely because the vault is locked.

Everything runs against a temp secrets dir with the crypto config rebound onto it, so no
real key material is read or written.
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
from solver.config import config as app_config
from solver.crypto import keys as keys_mod
from solver.crypto.ciphers import (enc_key_payload, load_private_key, public_key_hex,
                                   read_enc_key_file, read_master_key, verify_master_key)
from solver.crypto.config import config as crypto_config
from solver.shell import dialogue
from solver.web.msg import KEY_SHARE_SUBJECT, verb_for
from tests import silence

silence()   # these drive the console's refusal paths on purpose


def _keypair() -> tuple[x25519.X25519PrivateKey, str]:
    """A fresh X25519 pair and its public key hex."""
    private = x25519.X25519PrivateKey.generate()
    return private, public_key_hex(private.public_key())


class EncKeyTestCase(unittest.TestCase):
    """A throwaway secrets dir, with the enc-key file and private key rebound onto it."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.secrets = Path(self._tmp.name)
        self._saved = {key: crypto_config[key] for key in ('enc_key_file', 'private_key_file')}
        crypto_config['enc_key_file'] = self.secrets / 'enc-key.json'
        crypto_config['private_key_file'] = self.secrets / 'id'
        self.addCleanup(self._restore)
        self.master = token_bytes(32)
        self.mine_key, self.mine = _keypair()
        self.theirs_key, self.theirs = _keypair()
        self._be(self.mine_key)

    def _restore(self) -> None:
        for key, value in self._saved.items():
            crypto_config[key] = value
        self._tmp.cleanup()
        load_private_key.cache_clear()
        read_master_key.cache_clear()

    def _be(self, private: x25519.X25519PrivateKey) -> None:
        """Become the holder of *private* — the identity the read path resolves."""
        crypto_config['private_key_file'].write_bytes(private.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
        load_private_key.cache_clear()
        read_master_key.cache_clear()

    def _issue_to(self, public_key: x25519.X25519PublicKey) -> dict[str, str]:
        return enc_key_payload(public_key, self.master)


class ReadPathTests(EncKeyTestCase):
    """One file, one entry, and the same proof as ever."""

    def test_the_holders_key_unwraps_and_verifies(self) -> None:
        keys_mod.write_enc_key_file(self._issue_to(self.mine_key.public_key()))
        self.assertEqual(read_master_key(), self.master)

    def test_a_file_holding_somebody_elses_key_is_not_ours_to_open(self) -> None:
        keys_mod.write_enc_key_file(self._issue_to(self.theirs_key.public_key()))
        with self.assertRaises(KeyError):
            read_master_key()

    def test_no_file_is_simply_no_access(self) -> None:
        with self.assertRaises(FileNotFoundError):
            read_master_key()

    def test_a_payload_that_fails_verify_is_refused(self) -> None:
        """The proof is not optional: an entry that unwraps to the wrong key still fails."""
        payload = enc_key_payload(self.mine_key.public_key(), token_bytes(32))
        payload['verify'] = self._issue_to(self.mine_key.public_key())['verify']
        keys_mod.write_enc_key_file(payload)
        with self.assertRaises(ValueError):
            read_master_key()

    def test_a_payload_is_exactly_two_records(self) -> None:
        payload = self._issue_to(self.theirs_key.public_key())
        self.assertEqual(set(payload), {'verify', self.theirs})

    def test_the_file_is_written_private(self) -> None:
        keys_mod.write_enc_key_file(self._issue_to(self.mine_key.public_key()))
        self.assertEqual(crypto_config['enc_key_file'].stat().st_mode & 0o777, 0o600)


class SaveIssuedKeyTests(EncKeyTestCase):
    """`msg act` on a key message: prove the payload, then write — never the other way round."""

    def setUp(self) -> None:
        super().setUp()
        self._wired: list[str] = []
        import solver.core.git as git_mod
        saved = git_mod.enc_key_arrived
        # It now takes the local edits `save_issued_key` collected before the write, so the
        # stub has to accept them — see tests/test_rekey_rehome.py for what they are for.
        git_mod.enc_key_arrived = (          # type: ignore[assignment]
            lambda edits=None: self._wired.append('wired'))
        self.addCleanup(setattr, git_mod, 'enc_key_arrived', saved)

    def _message(self, payload: dict[str, str]) -> str:
        return keys_mod._issue_body(payload)

    def _master_on_disk(self) -> bytes:
        """Re-read the file, past `read_master_key`'s cache.

        These tests assert about the FILE — what a save did or refused to do to it — and a
        cached read answers about a moment before that. The cache is real behaviour (it is
        why `user` had to learn to clear it), so the test steps around it rather than
        pretending it is not there.
        """
        read_master_key.cache_clear()
        return read_master_key()

    def test_a_failed_save_leaves_the_message_alone(self) -> None:
        """Dismissal follows a *successful* act. A payload that did not prove out leaves the
        message where it is — it is the only copy of a key somebody has to re-issue."""
        keys_mod.write_enc_key_file(self._issue_to(self.mine_key.public_key()))
        self.assertFalse(keys_mod.save_issued_key(self._message(
            self._issue_to(self.theirs_key.public_key()))))
        self.assertEqual(self._master_on_disk(), self.master)

    def test_a_good_payload_is_saved_and_wires_the_filter(self) -> None:
        self.assertTrue(keys_mod.save_issued_key(self._message(
            self._issue_to(self.mine_key.public_key()))))
        self.assertEqual(self._master_on_disk(), self.master)
        self.assertEqual(self._wired, ['wired'], 'saving access must wire the filter')

    def test_a_payload_issued_to_somebody_else_is_refused(self) -> None:
        """The most likely real mistake: a maintainer works the wrong request."""
        keys_mod.write_enc_key_file(self._issue_to(self.mine_key.public_key()))
        self.assertFalse(keys_mod.save_issued_key(self._message(
            self._issue_to(self.theirs_key.public_key()))))
        self.assertEqual(self._master_on_disk(), self.master, 'our own file must survive intact')

    def test_a_payload_that_fails_verify_is_refused(self) -> None:
        payload = enc_key_payload(self.mine_key.public_key(), token_bytes(32))
        payload['verify'] = self._issue_to(self.mine_key.public_key())['verify']
        self.assertFalse(keys_mod.save_issued_key(self._message(payload)))
        self.assertFalse(crypto_config['enc_key_file'].exists(), 'nothing may be written')

    def test_a_message_with_no_payload_is_refused(self) -> None:
        self.assertFalse(keys_mod.save_issued_key('here you go, good luck'))

    def test_a_mangled_payload_is_refused(self) -> None:
        self.assertFalse(keys_mod.save_issued_key('{ "verify": not json }'))

    def test_the_payload_survives_the_prose_around_it(self) -> None:
        """The body is written for a person to read; the braces are the contract."""
        payload = self._issue_to(self.mine_key.public_key())
        body = f'Hello!\n\n{json.dumps(payload, indent=2)}\n\nRegards, the operator\n'
        self.assertTrue(keys_mod.save_issued_key(body))
        self.assertEqual(self._master_on_disk(), self.master)


class RegenTests(EncKeyTestCase):
    """`user --regen`: carry the master key when you hold it, ask for it when you do not."""

    def setUp(self) -> None:
        super().setUp()
        self.requests: list[tuple[str, str]] = []
        saved_request = keys_mod._request_authorization
        keys_mod._request_authorization = (                              # type: ignore[assignment]
            lambda identity, public_key: self.requests.append((identity, public_key)))
        self.addCleanup(setattr, keys_mod, '_request_authorization', saved_request)
        for name, stub in (('sure', lambda _q, *, phrase='': True),):
            saved = getattr(keys_mod, name)
            setattr(keys_mod, name, stub)
            self.addCleanup(setattr, keys_mod, name, saved)
        saved_emit, keys_mod.osc.emit = keys_mod.osc.emit, lambda *a, **k: None
        self.addCleanup(setattr, keys_mod.osc, 'emit', saved_emit)
        saved_subject = app_config.subject
        self.addCleanup(setattr, app_config, 'subject', saved_subject)

    def test_a_rotation_that_can_load_the_key_carries_it_and_asks_nobody(self) -> None:
        """Self-service, and the whole reason this file stopped being shared.

        The old design could not do this: the carry went into a *tracked* file, so it was a
        stopgap that still needed a maintainer to authorise the new key and land it.
        """
        keys_mod.write_enc_key_file(self._issue_to(self.mine_key.public_key()))
        before = public_key_hex(load_private_key().public_key())

        self.assertEqual(keys_mod.user(regen=True), 0)

        after = public_key_hex(load_private_key().public_key())
        self.assertNotEqual(before, after, 'the key pair must have rotated')
        self.assertEqual(read_master_key(), self.master, 'and access carried across')
        self.assertEqual(set(read_enc_key_file()), {'verify', after})
        self.assertEqual(self.requests, [], 'nothing to ask anyone for')

    def test_a_mint_with_no_master_key_files_a_request(self) -> None:
        self.assertEqual(keys_mod.user(regen=True), 0)
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(self.requests[0][1], public_key_hex(load_private_key().public_key()))

    def test_a_locked_vault_never_files_a_request(self) -> None:
        """A locked vault is not missing access — filing a request would have staff
        re-issuing to somebody who already holds the master key. The persist refuses first,
        which is what keeps that path unreachable; this pins it."""
        saved = keys_mod._create_user_key

        def refuse() -> x25519.X25519PrivateKey:
            raise PermissionError('vault locked')

        keys_mod._create_user_key = refuse                               # type: ignore[assignment]
        self.addCleanup(setattr, keys_mod, '_create_user_key', saved)
        self.assertEqual(keys_mod.user(regen=True), 1)
        self.assertEqual(self.requests, [], 'a locked vault must not look like missing access')


class PublicKeyRegistryTests(unittest.TestCase):
    """Registering a key for `key-rekey` is best-effort, and must fail quietly."""

    def test_a_shell_that_cannot_elevate_does_not_try(self) -> None:
        """A web shell's unit sets NoNewPrivileges, so sudo cannot work there — and does not
        merely fail, it prints two lines about container configuration at somebody who asked
        to authorise a key. Asking the kernel first turns that into a path not taken."""
        from solver.web.auth import commands as users_mod
        calls: list[tuple[str, ...]] = []
        for name, stub in (('_can_elevate', lambda: False),
                           ('_sudo_admin', lambda *a: calls.append(a) or 0)):
            saved = getattr(users_mod, name)
            setattr(users_mod, name, stub)
            self.addCleanup(setattr, users_mod, name, saved)
        self.assertFalse(users_mod.register_public_key('them@example.com', 'ab' * 32))
        self.assertEqual(calls, [], 'no sudo should be spawned at all')


class KeySplitTestCase(EncKeyTestCase):
    """A temp secrets dir as above, plus a temp *roster* and a spool that records."""

    def setUp(self) -> None:
        super().setUp()
        # Two real files this must never touch: the tracked roster in the checkout, and the
        # share, which on a deployed host is root-owned under /etc/euler — writing it there
        # would put a sudo prompt in the middle of a test run.
        self._saved_roster = os.environ.get(roster.ROSTER_FILE_ENV)
        os.environ[roster.ROSTER_FILE_ENV] = str(self.secrets / 'users.json')
        self._saved_share_file = crypto_config['share_file']
        crypto_config['share_file'] = self.secrets / 'share.json'
        self.addCleanup(self._restore_share)
        self.sent: list[tuple[str, str, str]] = []
        self._wired: list[str] = []
        import solver.core.git as git_mod
        import solver.web.msg.notify as notify_mod
        for module, name, stub in (
                (notify_mod, 'notify_user',
                 lambda identity, subject, body: bool(self.sent.append((identity, subject, body))
                                                      or True)),
                (git_mod, 'enc_key_arrived', lambda edits=None: self._wired.append('wired')),
                (keys_mod, 'sure', lambda _q, *, phrase='': True)):
            saved = getattr(module, name)
            setattr(module, name, stub)
            self.addCleanup(setattr, module, name, saved)

    def _record_key(self, identity: str, public_key: str) -> None:
        """Put a public key in the roster — what `users set-keys` does on the operator's box."""
        roster.upsert(identity, public_key=public_key, scope='web')

    def _restore_share(self) -> None:
        crypto_config['share_file'] = self._saved_share_file
        if self._saved_roster is None:
            os.environ.pop(roster.ROSTER_FILE_ENV, None)
        else:
            os.environ[roster.ROSTER_FILE_ENV] = self._saved_roster

    def _hold_the_master_key(self) -> None:
        """Become a holder: the enc-key file this machine can open, cache cleared."""
        keys_mod.write_enc_key_file(self._issue_to(self.mine_key.public_key()))
        read_master_key.cache_clear()

    def _lay_the_local_share(self) -> None:
        """The first `key-split` run: write this machine's half, send nothing."""
        self.assertEqual(keys_mod.key_split('them@example.com', self.mine), 0)
        self.assertEqual(self.sent, [], 'the laying run sends nothing')

    def _split_to(self, identity: str, public_key: str = '') -> str:
        """Run `key-split` for *identity* and return the **wrapped** share it sent."""
        self.assertEqual(keys_mod.key_split(identity, public_key or self.mine), 0)
        share = keys_mod.share_in_message(self.sent[-1][2])
        assert share is not None, 'the message must carry exactly one share'
        return share

    def _open(self, wrapped: str, private: x25519.X25519PrivateKey | None = None) -> str:
        """The share inside a wrapped blob, as its recipient reads it."""
        share = keys_mod._unwrap_share(private or self.mine_key, wrapped)
        assert share is not None, 'the blob must open with that private key'
        return share

    def _local_half(self) -> str:
        share = keys_mod.read_local_share()
        assert share is not None, 'this machine must hold a half'
        return share['share']


class KeySplitTests(KeySplitTestCase):
    """Two halves: one committed, one sealed to its recipient. The first run writes the committed one."""

    def test_the_first_run_writes_the_repository_share_and_sends_nothing(self) -> None:
        """A half nobody can complete is worse than no half: the repository's share has to be
        committable before anyone is sent the other one."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        self.assertTrue(crypto_config['share_file'].exists())

    def test_the_second_run_sends_a_share_under_the_share_subject(self) -> None:
        self._hold_the_master_key()
        self._lay_the_local_share()
        wrapped = self._split_to('them@example.com')
        identity, subject, _ = self.sent[-1]
        self.assertEqual(identity, 'them@example.com')
        self.assertTrue(subject.startswith(KEY_SHARE_SUBJECT), subject)
        self.assertEqual(verb_for(subject, is_staff=False, is_own=False), 'reconstruct')
        self.assertNotEqual(self._open(wrapped), self._local_half(), 'the two halves must differ')

    def test_the_message_carries_no_share_in_the_clear(self) -> None:
        """The point of wrapping: a spool reader (or anyone the message is forwarded to) holds
        a blob, and a blob plus a clone is nothing without the recipient's private key."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        wrapped = self._split_to('them@example.com')
        body = self.sent[-1][2]
        self.assertNotIn(self._open(wrapped), body, 'the plain share must not appear in the body')
        self.assertNotIn(self.master.hex(), body)
        self.assertIsNone(keys_mod._unwrap_share(self.theirs_key, wrapped),
                          'a different private key must not open it')

    def test_a_recipient_with_no_public_key_is_refused_before_anything_is_minted(self) -> None:
        """There is nothing to seal a half to, and sending it in the clear is not the fallback
        — a share plus a clone (which every collaborator has) is the master key."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        self.assertEqual(keys_mod.key_split('them@example.com'), 1)  # not in the roster at all
        self._record_key('them@example.com', '')                     # …or in it with no key
        self.assertEqual(keys_mod.key_split('them@example.com'), 1)
        self.assertEqual(self.sent, [], 'nothing may be sent')

    def test_the_roster_supplies_the_key_when_none_is_passed(self) -> None:
        """The ordinary path, and the reason the roster is tracked: `users set-keys` recorded
        the key, so the address is the only thing anyone has to type — from any clone, with no
        sudo, which is what a maintainer's web shell could never do."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        self._record_key('them@example.com', self.mine)
        self.assertEqual(keys_mod.key_split('them@example.com'), 0)
        share = self._open(self._share_sent())                       # sealed to the roster's key
        self.assertEqual(keys_mod._reconstruct_secret([self._local_half(), share]), self.master)

    def test_a_send_records_the_issue_against_the_recipient(self) -> None:
        """An act, dated: what the operator did, so a later rotation knows who to re-issue to.
        Not a claim that they still hold it — that fact lives in their own enc-key file."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        self._split_to('them@example.com')
        entry = roster.user_entry('them@example.com') or {}
        self.assertEqual(entry.get('public_key'), self.mine)
        self.assertTrue(entry.get('key_issued'), 'the issue must be dated')

    def test_the_roster_holds_no_e_mail_address(self) -> None:
        """Records are keyed by slug — the same decision that keeps addresses out of /home,
        the process table and branch names, applied to a file in a public repository."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        self._split_to('them@example.com')
        self.assertNotIn('them@example.com', roster.roster_path().read_text())
        self.assertIn(roster.slug_of('them@example.com'), roster.read_roster()['users'])

    def test_every_holder_gets_a_different_half_of_the_same_key(self) -> None:
        """One committed share completes for everybody, and no two of them receive the same
        thing — otherwise a share taken from one holder would be the one issued to the next."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        first = self._open(self._split_to('first@example.com'))
        second = self._open(self._split_to('second@example.com', self.mine))
        self.assertNotEqual(first, second)
        for share in (first, second):
            self.assertEqual(keys_mod._reconstruct_secret([self._local_half(), share]), self.master)

    def test_the_repository_share_alone_is_not_the_key(self) -> None:
        """The property the whole design rests on: the committed half is a random point, and
        the file carries nothing else that could stand in for the other half."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        stored = crypto_config['share_file'].read_text()
        self.assertNotIn(self.master.hex(), stored)
        self.assertEqual(set(keys_mod.read_local_share() or {}), {'share', 'verify', 'since'})

    def test_a_share_from_before_a_rotation_is_redrawn_rather_than_completed(self) -> None:
        """A half minted against a stale share reconstructs into the retired key, and the
        holder finds that out at the far end. `key-split` refuses to be that far end."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        stale = self._local_half()
        keys_mod.write_enc_key_file(enc_key_payload(self.mine_key.public_key(), token_bytes(32)))
        read_master_key.cache_clear()

        self.assertEqual(keys_mod.key_split('them@example.com', self.mine), 0)
        self.assertEqual(self.sent, [], 'a stale share is rewritten, not completed')
        self.assertNotEqual(self._local_half(), stale)

    def _share_sent(self) -> str:
        """The wrapped share in the most recent message."""
        share = keys_mod.share_in_message(self.sent[-1][2])
        assert share is not None
        return share


class KeyReconstructTests(KeySplitTestCase):
    """The receiving end: unwrap with your own key, then prove the halves before writing."""

    def test_the_two_halves_make_the_key_and_wire_the_filter(self) -> None:
        self._hold_the_master_key()
        self._lay_the_local_share()
        wrapped = self._split_to('them@example.com')
        crypto_config['enc_key_file'].unlink()                       # they hold nothing yet
        read_master_key.cache_clear()

        self.assertEqual(keys_mod.key_reconstruct(wrapped), 0)
        read_master_key.cache_clear()
        self.assertEqual(read_master_key(), self.master)
        self.assertEqual(self._wired, ['wired'], 'gaining access must wire the filter')

    def test_a_share_wrapped_to_somebody_else_is_refused(self) -> None:
        """The likeliest real mistake, and the one wrapping exists to catch: a maintainer
        seals a half to the wrong public key."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        wrapped = self._split_to('them@example.com', self.theirs)     # sealed to another key
        crypto_config['enc_key_file'].unlink()
        read_master_key.cache_clear()

        self.assertEqual(keys_mod.key_reconstruct(wrapped), 1)
        self.assertFalse(crypto_config['enc_key_file'].exists(), 'nothing may be written')

    def test_a_bare_share_still_works_by_hand(self) -> None:
        """The out-of-band path: a share read off another screen is not wrapped to anything,
        and refusing it would leave the manual route with nothing to type."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        bare = self._open(self._split_to('them@example.com'))
        crypto_config['enc_key_file'].unlink()
        read_master_key.cache_clear()

        self.assertEqual(keys_mod.key_reconstruct(bare), 0)
        read_master_key.cache_clear()
        self.assertEqual(read_master_key(), self.master)

    def test_a_wrong_share_is_caught_by_the_share_files_own_verify(self) -> None:
        """The machine that needs to reconstruct is the one with no enc-key file to check
        against — so the committed share carries the proof itself."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        wrong = keys_mod._counterpart(token_bytes(32), self._local_half())     # another secret
        crypto_config['enc_key_file'].unlink()
        read_master_key.cache_clear()

        self.assertEqual(keys_mod.key_reconstruct(wrong), 1)
        self.assertFalse(crypto_config['enc_key_file'].exists(), 'nothing may be written')

    def test_a_reconstruction_that_fails_verify_leaves_the_file_alone(self) -> None:
        self._hold_the_master_key()
        self._lay_the_local_share()
        good = read_enc_key_file()
        wrong = keys_mod._counterpart(token_bytes(32), self._local_half())

        self.assertEqual(keys_mod.key_reconstruct(wrong), 1)
        self.assertEqual(read_enc_key_file(), good, 'the working file must survive')
        self.assertTrue(verify_master_key(read_enc_key_file(), self.master))

    def test_a_clone_with_no_share_says_so_rather_than_reconstructing(self) -> None:
        self._hold_the_master_key()
        self._lay_the_local_share()
        wrapped = self._split_to('them@example.com')
        crypto_config['share_file'].unlink()
        self.assertEqual(keys_mod.key_reconstruct(wrapped), 1)

    def test_a_mistyped_share_is_refused_on_shape(self) -> None:
        self._hold_the_master_key()
        self._lay_the_local_share()
        wrapped = self._split_to('them@example.com')
        for bad in (wrapped[:-2], wrapped + 'ab', wrapped[:-1] + 'z'):
            with self.subTest(bad=bad[-8:]):
                self.assertEqual(keys_mod.key_reconstruct(bad), 1)
        with self.assertRaises(dialogue.Abort):                      # nothing given at all
            keys_mod.key_reconstruct('')

    def test_the_share_survives_the_prose_around_it(self) -> None:
        """As with an issued key, the body is written for a person; the run of hex is the
        contract `msg act` reads it under."""
        self._hold_the_master_key()
        self._lay_the_local_share()
        wrapped = self._split_to('them@example.com')
        self.assertEqual(keys_mod.share_in_message(f'Hi!\n\nshare: {wrapped}\n\nRegards\n'), wrapped)
        self.assertIsNone(keys_mod.share_in_message('no share here, sorry'))
        self.assertIsNone(keys_mod.share_in_message(f'{wrapped}\n{wrapped[:-1]}f\n'))


if __name__ == '__main__':
    unittest.main()
