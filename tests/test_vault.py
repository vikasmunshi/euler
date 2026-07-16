#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The per-user vault (`solver.crypto.vault`): envelope encryption of `id` + `env`.

Covers the primitives (PBKDF2 password key, wrap/unwrap the vault key, secret encrypt/decrypt),
the vault file lifecycle (init / unlock / change-password), session-key delivery (tmpfs key file
and the terminal `user_pass` fallback), and the two integration points that must transparently
decrypt the vault form: `load_private_key` (crypto) and `get_api_key` (ai).

Everything is redirected onto a temp directory by rebinding the paths in the crypto/app config dicts,
so no real `~/.euler` is touched and the suite is host-independent.
"""
from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from solver.ai import models
from solver.config import config as app_config
from solver.crypto import ciphers, vault
from solver.crypto.config import config as crypto_config


class VaultTestCase(unittest.TestCase):
    """Base: a throwaway `~/.euler` with every vault path rebound onto it, and caches cleared."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.secrets = Path(self._tmp.name)
        self.id_file = self.secrets / 'id'
        self.env_file = self.secrets / 'env'
        # Rebind the crypto config to the temp secrets dir.
        self._saved_crypto = {k: crypto_config[k] for k in
                              ('private_key_file', 'env_file', 'vault_file', 'user_pass_file')}
        crypto_config['private_key_file'] = self.id_file
        crypto_config['env_file'] = self.env_file
        crypto_config['vault_file'] = self.secrets / 'vault'
        crypto_config['user_pass_file'] = self.secrets / 'user_pass'
        # ai.models reads solver.config.env_file for the Anthropic key.
        self._saved_env_file = app_config.env_file
        app_config.env_file = self.env_file
        # A cheap KDF so the suite is fast; the primitive is unchanged.
        self._saved_iters = crypto_config['vault_kdf_iterations']
        crypto_config['vault_kdf_iterations'] = 1000
        self._saved_key_env = os.environ.pop(crypto_config['vault_key_env'], None)
        self._clear_caches()

    def tearDown(self) -> None:
        for k, v in self._saved_crypto.items():
            crypto_config[k] = v
        app_config.env_file = self._saved_env_file
        crypto_config['vault_kdf_iterations'] = self._saved_iters
        os.environ.pop(crypto_config['vault_key_env'], None)
        if self._saved_key_env is not None:
            os.environ[crypto_config['vault_key_env']] = self._saved_key_env
        self._clear_caches()
        self._tmp.cleanup()

    @staticmethod
    def _clear_caches() -> None:
        vault._resolve_session_key.cache_clear()
        ciphers.load_private_key.cache_clear()
        models.get_api_key.cache_clear()

    def _write_plain_key(self) -> x25519.X25519PrivateKey:
        """Write a fresh plaintext PKCS8 private key to the id file; return it."""
        key = x25519.X25519PrivateKey.generate()
        self.id_file.write_bytes(key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
        return key


class PrimitivesTest(VaultTestCase):
    def test_password_key_is_deterministic_and_password_sensitive(self) -> None:
        salt = b'\x01' * 16
        pk = vault.derive_password_key('hunter2', salt, 1000)
        self.assertEqual(len(pk), 32)
        self.assertEqual(pk, vault.derive_password_key('hunter2', salt, 1000))
        self.assertNotEqual(pk, vault.derive_password_key('hunter3', salt, 1000))
        self.assertNotEqual(pk, vault.derive_password_key('hunter2', b'\x02' * 16, 1000))

    def test_wrap_unwrap_roundtrip_and_wrong_key_fails(self) -> None:
        pk = vault.derive_password_key('pw', b'salt-salt-salt!!', 1000)
        vk = vault.new_vault_key()
        wrapped = vault.wrap_vault_key(pk, vk)
        self.assertEqual(vault.unwrap_vault_key(pk, wrapped), vk)
        wrong = vault.derive_password_key('nope', b'salt-salt-salt!!', 1000)
        with self.assertRaises(InvalidTag):
            vault.unwrap_vault_key(wrong, wrapped)

    def test_secret_roundtrip_header_and_passthrough(self) -> None:
        vk = vault.new_vault_key()
        blob = vault.encrypt_secret(vk, b'top secret')
        self.assertTrue(vault.is_vault_encrypted(blob))
        self.assertNotIn(b'top secret', blob)
        self.assertEqual(vault.decrypt_secret(vk, blob), b'top secret')
        # Idempotent on already-encrypted input, pass-through on plaintext.
        self.assertEqual(vault.encrypt_secret(vk, blob), blob)
        self.assertFalse(vault.is_vault_encrypted(b'plain'))
        self.assertEqual(vault.decrypt_secret(vk, b'plain'), b'plain')

    def test_wrong_vault_key_cannot_decrypt_secret(self) -> None:
        blob = vault.encrypt_secret(vault.new_vault_key(), b'data')
        with self.assertRaises(InvalidTag):
            vault.decrypt_secret(vault.new_vault_key(), blob)


class VaultFileTest(VaultTestCase):
    def test_init_then_unlock(self) -> None:
        vk = vault.init_vault('correct horse')
        self.assertTrue(vault.vault_exists())
        self.assertEqual(vault.unlock_vault('correct horse'), vk)
        with self.assertRaises(InvalidTag):
            vault.unlock_vault('wrong')

    def test_unlock_without_vault_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            vault.unlock_vault('anything')

    def test_change_password_preserves_vault_key(self) -> None:
        vk = vault.init_vault('old-pw')
        vault.rewrap_vault('old-pw', 'new-pw')
        self.assertEqual(vault.unlock_vault('new-pw'), vk)
        with self.assertRaises(InvalidTag):
            vault.unlock_vault('old-pw')

    def test_vault_file_is_0600(self) -> None:
        vault.init_vault('pw')
        self.assertEqual(crypto_config['vault_file'].stat().st_mode & 0o777, 0o600)


class SessionKeyTest(VaultTestCase):
    def test_session_key_from_tmpfs_file(self) -> None:
        vk = vault.new_vault_key()
        path = vault.write_session_key(vk)
        self.addCleanup(lambda: path.exists() and path.unlink())
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(os.environ[crypto_config['vault_key_env']], str(path))
        self.assertEqual(vault.session_vault_key(), vk)

    def test_session_key_from_user_pass_fallback(self) -> None:
        vk = vault.init_vault('terminal-pw')
        crypto_config['user_pass_file'].write_text('terminal-pw')
        # No key file set: must derive VK from user_pass.
        self.assertNotIn(crypto_config['vault_key_env'], os.environ)
        self.assertEqual(vault.session_vault_key(), vk)

    def test_locked_when_no_key_and_no_user_pass(self) -> None:
        vault.init_vault('pw')  # vault exists, but neither key file nor user_pass present
        self.assertIsNone(vault.session_vault_key())

    def test_ensure_session_key_materialises_file_from_user_pass(self) -> None:
        vk = vault.init_vault('pw')
        crypto_config['user_pass_file'].write_text('pw')
        got = vault.ensure_session_key()
        self.assertEqual(got, vk)
        key_path = Path(os.environ[crypto_config['vault_key_env']])
        self.addCleanup(lambda: key_path.exists() and key_path.unlink())
        self.assertEqual(key_path.read_bytes(), vk)


class LoadPrivateKeyIntegrationTest(VaultTestCase):
    def test_plaintext_key_still_loads(self) -> None:
        key = self._write_plain_key()
        loaded = ciphers.load_private_key()
        self.assertEqual(ciphers.public_key_hex(loaded.public_key()),
                         ciphers.public_key_hex(key.public_key()))

    def test_vault_encrypted_key_loads_when_unlocked(self) -> None:
        key = self._write_plain_key()
        vk = vault.init_vault('pw')
        # Encrypt the id file in place, as `vault init` does.
        self.id_file.write_bytes(vault.encrypt_secret(vk, self.id_file.read_bytes()))
        self.assertTrue(vault.is_vault_encrypted(self.id_file.read_bytes()))
        path = vault.write_session_key(vk)
        self.addCleanup(lambda: path.exists() and path.unlink())
        ciphers.load_private_key.cache_clear()
        loaded = ciphers.load_private_key()
        self.assertEqual(ciphers.public_key_hex(loaded.public_key()),
                         ciphers.public_key_hex(key.public_key()))

    def test_vault_encrypted_key_fails_clearly_when_locked(self) -> None:
        self._write_plain_key()
        vk = vault.init_vault('pw')
        self.id_file.write_bytes(vault.encrypt_secret(vk, self.id_file.read_bytes()))
        ciphers.load_private_key.cache_clear()
        with self.assertRaises(ValueError) as ctx:
            ciphers.load_private_key()
        self.assertIn('vault is locked', str(ctx.exception))


class GetApiKeyIntegrationTest(VaultTestCase):
    def test_plaintext_env_still_read(self) -> None:
        self.env_file.write_text('ANTHROPIC_API_KEY=sk-plain-123\n')
        self.assertEqual(models.get_api_key(), 'sk-plain-123')

    def test_vault_encrypted_env_decrypts_when_unlocked(self) -> None:
        vk = vault.init_vault('pw')
        self.env_file.write_bytes(vault.encrypt_secret(vk, b'ANTHROPIC_API_KEY=sk-secret-xyz\n'))
        path = vault.write_session_key(vk)
        self.addCleanup(lambda: path.exists() and path.unlink())
        models.get_api_key.cache_clear()
        self.assertEqual(models.get_api_key(), 'sk-secret-xyz')

    def test_vault_encrypted_env_fails_when_locked(self) -> None:
        vk = vault.init_vault('pw')
        self.env_file.write_bytes(vault.encrypt_secret(vk, b'ANTHROPIC_API_KEY=sk-secret-xyz\n'))
        models.get_api_key.cache_clear()
        with self.assertRaises(ValueError) as ctx:
            models.get_api_key()
        self.assertIn('vault is locked', str(ctx.exception))


class PkVaultTest(VaultTestCase):
    """The web path: PK-taking twins of the password functions."""

    _SALT = b'\x0a' * 16

    def _pk(self, password: str, salt: bytes | None = None) -> bytes:
        return vault.derive_password_key(password, salt or self._SALT, 1000)

    def test_init_from_pk_then_unlock_with_pk(self) -> None:
        pk = self._pk('pw')
        vk = vault.init_vault_from_pk(pk, self._SALT)
        self.assertTrue(vault.vault_exists())
        self.assertEqual(vault.unlock_vault_with_pk(pk), vk)
        # The recorded salt is the SRP salt, so the terminal path derives the same PK.
        data = vault.read_vault()
        assert data is not None
        self.assertEqual(data['salt'], self._SALT.hex())
        with self.assertRaises(InvalidTag):
            vault.unlock_vault_with_pk(self._pk('wrong'))

    def test_init_from_pk_encrypts_existing_plaintext_secrets(self) -> None:
        self._write_plain_key()
        self.env_file.write_text('ANTHROPIC_API_KEY=sk-plain\n')
        vk = vault.init_vault_from_pk(self._pk('pw'), self._SALT)
        for path in (self.id_file, self.env_file):
            self.assertTrue(vault.is_vault_encrypted(path.read_bytes()))
        self.assertIn(b'sk-plain', vault.decrypt_secret(vk, self.env_file.read_bytes()))

    def test_rewrap_with_pk_survives_a_password_change(self) -> None:
        new_salt = b'\x0b' * 16
        old_pk, new_pk = self._pk('old-pw'), self._pk('new-pw', new_salt)
        vk = vault.init_vault_from_pk(old_pk, self._SALT)
        vault.rewrap_vault_with_pk(old_pk, new_pk, new_salt)
        self.assertEqual(vault.unlock_vault_with_pk(new_pk), vk)   # same VK: secrets untouched
        with self.assertRaises(InvalidTag):
            vault.unlock_vault_with_pk(old_pk)
        data = vault.read_vault()
        assert data is not None
        self.assertEqual(data['salt'], new_salt.hex())

    def test_rewrap_with_wrong_old_pk_fails(self) -> None:
        vault.init_vault_from_pk(self._pk('pw'), self._SALT)
        with self.assertRaises(InvalidTag):
            vault.rewrap_vault_with_pk(self._pk('wrong'), self._pk('new'), self._SALT)

    def test_reset_removes_vault_and_ciphertext_only(self) -> None:
        vk = vault.init_vault_from_pk(self._pk('pw'), self._SALT)
        self.id_file.write_bytes(vault.encrypt_secret(vk, b'PEM'))
        self.env_file.write_text('PLAIN=still-here\n')          # plaintext: never this vault's
        vault.write_session_key(vk)
        removed = vault.reset_vault()
        self.assertEqual(sorted(removed), ['id', 'vault'])
        self.assertFalse(vault.vault_exists())
        self.assertFalse(self.id_file.exists())
        self.assertEqual(self.env_file.read_text(), 'PLAIN=still-here\n')
        self.assertIsNone(vault.session_vault_key())            # the session is locked too

    def test_clear_session_key_removes_file_and_env(self) -> None:
        path = vault.write_session_key(vault.new_vault_key())
        self.assertTrue(path.exists())
        vault.clear_session_key()
        self.assertFalse(path.exists())
        self.assertNotIn(crypto_config['vault_key_env'], os.environ)
        self.assertIsNone(vault.session_vault_key())
        vault.clear_session_key()                               # idempotent


class PersistPrivateKeyTest(VaultTestCase):
    """`user --regen` follow-up: a regenerated key is written vault-encrypted, never plain beside a vault."""

    def test_persist_encrypts_under_the_session_vk(self) -> None:
        from solver.crypto.keys import _persist_private_key
        vk = vault.init_vault('pw')
        vault.write_session_key(vk)
        _persist_private_key(x25519.X25519PrivateKey.generate())
        raw = self.id_file.read_bytes()
        self.assertTrue(vault.is_vault_encrypted(raw))
        self.assertTrue(vault.decrypt_secret(vk, raw).startswith(b'-----BEGIN PRIVATE KEY-----'))

    def test_persist_refuses_when_the_vault_is_locked(self) -> None:
        from solver.crypto.keys import _persist_private_key
        vault.init_vault('pw')
        vault.clear_session_key()
        with self.assertRaises(PermissionError):
            _persist_private_key(x25519.X25519PrivateKey.generate())

    def test_persist_stays_plain_without_a_vault(self) -> None:
        from solver.crypto.keys import _persist_private_key
        _persist_private_key(x25519.X25519PrivateKey.generate())
        self.assertTrue(self.id_file.read_bytes().startswith(b'-----BEGIN PRIVATE KEY-----'))


class VaultFailureIsNeverANewIdentityTest(VaultTestCase):
    """The fragility class: an id that EXISTS but cannot be read (locked vault, stale
    session key, lost vault file) is a vault failure to fix — never 'no key, mint one'."""

    def _encrypted_id(self) -> tuple[bytes, bytes]:
        """A vault + a vault-encrypted id; returns (vk, the id file's bytes)."""
        vk = vault.init_vault('pw')
        key = self._write_plain_key()
        del key
        self.id_file.write_bytes(vault.encrypt_secret(vk, self.id_file.read_bytes()))
        return vk, self.id_file.read_bytes()

    def test_stale_session_key_is_unreadable_not_absent(self) -> None:
        self._encrypted_id()
        vault.write_session_key(vault.new_vault_key())      # a WRONG key in the session
        with self.assertRaises(ValueError) as ctx:          # ValueError, never InvalidTag
            ciphers.load_private_key()
        self.assertIn('does not decrypt', str(ctx.exception))

    def test_user_command_refuses_to_mint_over_a_locked_id(self) -> None:
        from solver.crypto.keys import user
        _, original = self._encrypted_id()
        vault.clear_session_key()                           # locked
        self._clear_caches()
        self.assertEqual(user(), 1)
        self.assertEqual(self.id_file.read_bytes(), original)   # byte-identical
        self.assertFalse(self.id_file.with_suffix('.1').exists())  # no rotation either

    def test_refused_persist_leaves_the_id_in_place(self) -> None:
        from solver.crypto.keys import _persist_private_key
        _, original = self._encrypted_id()
        vault.clear_session_key()
        self._clear_caches()
        with self.assertRaises(PermissionError):
            _persist_private_key(x25519.X25519PrivateKey.generate())
        self.assertEqual(self.id_file.read_bytes(), original)   # not rotated away
        self.assertFalse(self.id_file.with_suffix('.1').exists())

    def test_orphaned_vault_files_are_detected_and_block_init(self) -> None:
        from solver.crypto.keys import _orphaned_vault_files, vault as vault_cmd
        vk, _ = self._encrypted_id()
        self.env_file.write_bytes(vault.encrypt_secret(vk, b'ANTHROPIC_API_KEY=sk-x\n'))
        crypto_config['vault_file'].unlink()                # the vault file is LOST
        vault.clear_session_key()
        self._clear_caches()
        self.assertEqual(sorted(_orphaned_vault_files()), ['env', 'id'])
        self.assertEqual(vault_cmd('init'), 1)              # refuses to paper over it
        self.assertFalse(vault.vault_exists())

    def test_stale_session_key_on_env_is_unreadable_not_missing(self) -> None:
        vk = vault.init_vault('pw')
        self.env_file.write_bytes(vault.encrypt_secret(vk, b'ANTHROPIC_API_KEY=sk-x\n'))
        vault.write_session_key(vault.new_vault_key())      # wrong key
        models.get_api_key.cache_clear()
        with self.assertRaises(ValueError) as ctx:
            models.get_api_key()
        self.assertIn('does not decrypt', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
