#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""X25519 ECDH key pair generation, master key wrapping, and user identity management."""
from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

from solver.config import private_key_file
from solver.utils import get_gh_user_email


class UserKeyPair(NamedTuple):
    """
    An X25519 key pair used to wrap and unwrap the AES master key for a specific user.

    The private key lives only in the local key file (~/.ssh/id_solver). The public key
    and the user's encrypted copy of the master key are stored in keys.json.
    """

    user_email: str
    public_key: X25519PublicKey
    private_key: X25519PrivateKey | None
    is_admin_key: bool = False

    def __str__(self) -> str:
        """Return a human-readable summary showing the email, public key hex, and private key availability."""
        return (f'{self.__class__.__name__}(email={self.user_email}, '
                f'public_key={self.public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()} '
                f'private_key={self.private_key is not None})')

    @classmethod
    def new_ephemeral(cls, user_email: str | None = None) -> UserKeyPair:
        """
        Generate a transient X25519 key pair that is not written to disk.

        Args:
            user_email: Email to associate with the key pair; defaults to the authenticated GitHub user email.

        Returns:
            A UserKeyPair with both public and private keys populated.
        """
        email: str = user_email or get_gh_user_email()
        private_key: X25519PrivateKey = x25519.X25519PrivateKey.generate()
        public_key: X25519PublicKey = private_key.public_key()
        return cls(user_email=email, public_key=public_key, private_key=private_key)

    @classmethod
    def new_persistent(cls, user_email: str | None = None) -> UserKeyPair:
        """
        Generate a new X25519 key pair and persist the private key to disk.

        Up to five rolling backups of the existing private key file are kept.

        Args:
            user_email: Email to associate with the key pair; defaults to the authenticated GitHub user email.

        Returns:
            A UserKeyPair with both public and private keys populated.
        """
        email: str = user_email or get_gh_user_email()
        private_key: X25519PrivateKey = x25519.X25519PrivateKey.generate()
        public_key: X25519PublicKey = private_key.public_key()
        new: UserKeyPair = cls(user_email=email, public_key=public_key, private_key=private_key)
        new.to_file()
        return new

    @classmethod
    def from_file(cls) -> UserKeyPair:
        """
        Load the user key pair from the private key file on disk.

        Returns:
            A UserKeyPair with both public and private keys populated.

        Raises:
            FileNotFoundError: If the private key file does not exist.
        """
        if not private_key_file.exists():
            raise FileNotFoundError(f'Private key file {private_key_file} not found')
        with private_key_file.open('r') as f:
            user_email, private_hex = f.read().strip().split(maxsplit=1)
        private_key: X25519PrivateKey = x25519.X25519PrivateKey.from_private_bytes(bytes.fromhex(private_hex))
        return cls(user_email=user_email, private_key=private_key, public_key=private_key.public_key())

    def to_file(self, key_file: Path = private_key_file) -> None:
        """
        Write the private key to key_file, rotating up to five existing backups.

        The parent directory is created with mode 0o700 if it does not exist.
        Does nothing if private_key is None.

        Args:
            key_file: Destination file path. Defaults to ~/.ssh/id_solver.
        """
        if self.private_key is None:
            return
        if key_file.exists():
            for i in range(5, 0, -1):
                old_backup = key_file.with_suffix(f'.{i}')
                new_backup = key_file.with_suffix(f'.{i + 1}')
                if old_backup.exists():
                    old_backup.rename(new_backup)
                    print(f'Backed up existing private key file {key_file} to {old_backup}')
            backup_file = key_file.with_suffix('.1')
            key_file.rename(backup_file)
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key_file.parent.chmod(0o700)
        with key_file.open('w') as f:
            private_hex: str = self.private_key.private_bytes(encoding=Encoding.Raw,
                                                              format=PrivateFormat.Raw,
                                                              encryption_algorithm=NoEncryption()).hex()
            f.write(f'{self.user_email} {private_hex}\n')
            print(f'Private key file {key_file} initialized')

    @classmethod
    def from_public_dict(cls, email: str, data: dict[str, str]) -> UserKeyPair:
        """Deserialize a public-only UserKeyPair from its keys.json user entry (private_key is None)."""
        public_key: X25519PublicKey = X25519PublicKey.from_public_bytes(bytes.fromhex(data['public_key']))
        return cls(user_email=email, public_key=public_key, private_key=None)

    def to_public_dict(self, master_key: bytes | None = None) -> dict[str, str | None]:
        """Serialize the public key and optionally the locked master key to a keys.json user entry dict."""
        return {'public_key': self.public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex(),
                'master_key': self.lock(master_key) if master_key else None, }

    def lock(self, master_key: bytes) -> str:
        """
        Encrypt master_key so that only the holder of this key pair's private key can decrypt it.

        Uses an ephemeral X25519 key exchange followed by HKDF-SHA256 key derivation and
        ChaCha20-Poly1305 encryption. The ephemeral public key is prepended to the ciphertext.

        Args:
            master_key: The 32-byte master key to encrypt.

        Returns:
            Hex string of (32-byte ephemeral public key | ChaCha20-Poly1305 ciphertext).
        """
        ephemeral: UserKeyPair = self.__class__.new_ephemeral()
        assert ephemeral.private_key is not None, 'Ephemeral private key should be available'
        shared_secret: bytes = ephemeral.private_key.exchange(self.public_key)
        derived: bytes = HKDF(algorithm=SHA256(), length=32, salt=None, info=b'key-encryption').derive(shared_secret)
        cipher: ChaCha20Poly1305 = ChaCha20Poly1305(derived)
        nonce: bytes = b'\x00' * 12
        ciphertext: bytes = cipher.encrypt(nonce, master_key, None)
        ephemeral_public: bytes = ephemeral.public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)
        return (ephemeral_public + ciphertext).hex()

    def unlock(self, enc_master_key: str) -> bytes:
        """
        Decrypt the master key previously locked with lock().

        Args:
            enc_master_key: Hex string produced by lock(), containing the ephemeral public key
                            and ChaCha20-Poly1305 ciphertext.

        Returns:
            The decrypted 32-byte master key.

        Raises:
            ValueError: If private_key is None (public-only key pair cannot decrypt).
        """
        if self.private_key is None:
            raise ValueError('Cannot unlock using a KeyPair with null private key.')
        encrypted_bytes: bytes = bytes.fromhex(enc_master_key)
        ciphertext: bytes = encrypted_bytes[32:]
        ephemeral_public: X25519PublicKey = x25519.X25519PublicKey.from_public_bytes(encrypted_bytes[:32])
        shared_secret: bytes = self.private_key.exchange(ephemeral_public)
        derived: bytes = HKDF(algorithm=SHA256(), length=32, salt=None, info=b'key-encryption').derive(shared_secret)
        cipher: ChaCha20Poly1305 = ChaCha20Poly1305(derived)
        nonce: bytes = b'\x00' * 12
        return cipher.decrypt(nonce, ciphertext, None)


__all__ = ('UserKeyPair',)
