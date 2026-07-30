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
- `msg save` — it must **prove** a payload before overwriting the file that may be the only
  thing between this machine and the private tree;
- `user --regen` — carry the master key when it can be loaded, ask for it when it cannot,
  and never ask merely because the vault is locked.

Everything runs against a temp secrets dir with the crypto config rebound onto it, so no
real key material is read or written.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from secrets import token_bytes
from tempfile import TemporaryDirectory

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from solver.config import config as app_config
from solver.crypto import keys as keys_mod
from solver.crypto.ciphers import (enc_key_payload, load_private_key, public_key_hex,
                                   read_enc_key_file, read_master_key, verify_master_key)
from solver.crypto.config import config as crypto_config
from solver.shell import dialogue
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
    """`msg save`: prove the payload, then write — never the other way round."""

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


class KeyReconstructTests(EncKeyTestCase):
    """Shares are typed by hand, so a wrong reconstruction must not overwrite a good file."""

    def test_a_reconstruction_that_fails_verify_leaves_the_file_alone(self) -> None:
        good = self._issue_to(self.mine_key.public_key())
        keys_mod.write_enc_key_file(good)
        shares = keys_mod._split_secret(token_bytes(32), 3, 2)           # a DIFFERENT secret
        answers = iter(shares[:2])
        saved, keys_mod.console.input = keys_mod.console.input, lambda *a, **k: next(answers)
        self.addCleanup(setattr, keys_mod.console, 'input', saved)
        saved_interactive, dialogue.interactive = dialogue.interactive, lambda: True
        self.addCleanup(setattr, dialogue, 'interactive', saved_interactive)

        self.assertEqual(keys_mod.key_reconstruct(2), 1)
        self.assertEqual(read_enc_key_file(), good, 'the working file must survive')
        self.assertTrue(verify_master_key(read_enc_key_file(), self.master))


if __name__ == '__main__':
    unittest.main()
