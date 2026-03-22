#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""AES-GCM encryption and secure offline key exchange for sensitive problem data.

Provides AES-256-GCM authenticated encryption and ECC-based offline key distribution.

## Public API

    decrypt(cypher_text, *, key=None, aad=None) -> bytes
        Decrypt AES-256-GCM data with optional AAD verification

    encrypt(plain_text, *, key=None, aad=None) -> bytes
        Encrypt data using AES-256-GCM with optional AAD binding

    key_exchange() -> bool
        Orchestrate 3-step key exchange protocol (returns True if key obtained)

    vault_main(mode: str) -> None
        Execute vault operations from CLI (modes: 'user', 'process', 'new', 'verify')

## Command Line

    python solver/vault.py user      # End user: automatic key exchange
    python solver/vault.py process   # Maintainer: process key requests
    python solver/vault.py new       # Generate new encryption key
    python solver/vault.py verify    # Run integration test

## Encryption Details

    Algorithm:       AES-256-GCM (authenticated encryption with additional data)
    Key size:        256 bits (32 bytes)
    Nonce:           96 bits (12 bytes, randomly generated per encryption)
    Authentication:  128-bit tag (included in ciphertext)
    Key derivation:  SHA-256(key_file_content)
    Format:          base64([12-byte nonce][ciphertext+tag])
    AAD support:     Optional metadata binding (authenticated, not encrypted)

## Key Exchange Protocol

    Step 1 (Requestor):
        - Generate SECP384R1 keypair, save private key
        - Email public key to maintainer

    Step 2 (Maintainer):
        - Generate ephemeral SECP384R1 keypair
        - Derive shared key via ECDH + HKDF-SHA256
        - Encrypt the key file with AAD = requestor's public key (DER)
        - Email the ephemeral public key plus the encrypted key

    Step 3 (Requestor):
        - Derive shared key using the private key plus the ephemeral public key
        - Decrypt with AAD = own public key (DER)
        - Clean up temporary files

## Security Properties

    Confidentiality:   AES-256-GCM prevents unauthorized data access
    Authenticity:      GCM tag prevents ciphertext tampering
    Identity binding:  AAD ties encrypted key to recipient's public key
    Forward secrecy:   Ephemeral keys prevent past decryption if compromised
    Key strength:      SECP384R1 provides 192-bit security level

## File Structure

    keys/
    ├── key.txt          # Main encryption key (SHA-256 hashed for use)
    ├── private_key.pem  # Temporary: requestor's ECC private key
    ├── request.txt      # Temporary: email with requestor's public key
    └── response.txt     # Temporary: email with the encrypted key from maintainer

Author: Vikas Munshi <vikas.munshi@gmail.com>
Repository: https://github.com/vikasmunshi/euler
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from secrets import token_bytes, token_hex
from typing import Literal

from cryptography.hazmat.primitives import hashes, serialization  # pip install cryptography
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, EllipticCurvePublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from solver.workspace import BASE_DIR

__all__ = ['decrypt', 'encrypt', 'key_exchange', 'vault_main']

# Encryption/Key exchange constants
_key_file: Path = BASE_DIR / 'keys' / 'key.txt'  # Main encryption key file
_key_size: int = 32  # AES-256 requires 32 bytes (256 bits)
_private_key_file: Path = _key_file.parent / 'private_key.pem'
_request_file: Path = _key_file.parent / 'request.txt'
_response_file: Path = _key_file.parent / 'response.txt'
repo: str = 'https://github.com/vikasmunshi/euler'
contact: str = 'vikas.munshi@gmail.com'


# ============================================================================
# Public API - Encryption/Decryption
# ============================================================================

def decrypt(cypher_text: bytes, *, key: bytes = None, aad: bytes = None) -> bytes:
    """Decrypt AES-256-GCM encrypted data.

    Args:
        cypher_text: Base64-encoded encrypted data (nonce + ciphertext + tag)
        key: 32-byte AES-256 key (default: SHA-256 hash of keys/key.txt)
        aad: Associated Authenticated Data (must match encryption AAD or None)

    Returns:
        Decrypted plaintext bytes

    Raises:
        ValueError: If authentication fails (wrong key, tampered data, or AAD mismatch)
    """
    key = key or _get_key()
    combined: bytes = b64decode(cypher_text)
    nonce: bytes = combined[:12]
    ciphertext: bytes = combined[12:]
    return AESGCM(key).decrypt(nonce, ciphertext, aad)


def encrypt(plain_text: bytes, *, key: bytes = None, aad: bytes = None) -> bytes:
    """Encrypt data using AES-256-GCM with optional AAD binding.

    Args:
        plain_text: Data to encrypt (arbitrary bytes)
        key: 32-byte AES-256 key (default: SHA-256 hash of keys/key.txt)
        aad: Associated Authenticated Data (authenticated but not encrypted, e.g., metadata)

    Returns:
        Base64-encoded encrypted data: base64(nonce + ciphertext + auth_tag)

    Note:
        AAD binds metadata to ciphertext. Decryption requires identical AAD or None.
    """
    key = key or _get_key()
    nonce = token_bytes(12)
    ciphertext = AESGCM(key).encrypt(nonce, plain_text, aad)
    return b64encode(nonce + ciphertext)


# ============================================================================
# Public API - Key Exchange
# ============================================================================

def key_exchange() -> bool:
    """Orchestrate the 3-step key exchange process.

    Flow:
    - If key_file exists: Nothing to do, return True
    - If response_file exists: Step 3 (decrypt), return True
    - Otherwise: Step 1 (create request), return False

    Returns:
        True if the key was obtained, False if a request was created
    """
    if _key_file.exists():
        return True
    if _response_file.exists():
        _process_response()
        return True
    _create_request()
    return False


# ============================================================================
# Private Helpers - Cryptographic Utilities
# ============================================================================

def _create_shared_key(private_key: EllipticCurvePrivateKey, public_key: EllipticCurvePublicKey) -> bytes:
    """Perform ECDH key exchange and derive AES-256 key.

    Args:
        private_key: Local ECC private key
        public_key: Remote ECC public key

    Returns:
        32-byte derived key suitable for AES-256-GCM
    """
    shared_key = private_key.exchange(ec.ECDH(), public_key)
    derived_key: bytes = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'key-exchange').derive(shared_key)
    return derived_key


def _decode_publickey(pem_block: str) -> EllipticCurvePublicKey:
    """Reconstruct and load the ECC public key from PEM data.

    Args:
        pem_block: Base64-encoded public key data (without markers)

    Returns:
        EllipticCurvePublicKey object
    """
    pem_full: str = f'-----BEGIN PUBLIC KEY-----\n{pem_block}\n-----END PUBLIC KEY-----'
    public_key: EllipticCurvePublicKey = serialization.load_pem_public_key(pem_full.encode('utf-8'))
    return public_key


def _extract_pem_block(content: str, marker: str) -> str | None:
    """Extract text between PEM-style markers.

    Args:
        content: Text containing PEM blocks
        marker: Block type (e.g., 'PUBLIC KEY', 'ENCRYPTED KEY')

    Returns:
        Text between markers, or None if not found
    """
    start_marker = f'-----BEGIN {marker}-----'
    end_marker = f'-----END {marker}-----'
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    if start_idx == -1 or end_idx == -1:
        return None
    return content[start_idx + len(start_marker):end_idx].strip()


# ============================================================================
# Private Helpers - Key Exchange Steps
# ============================================================================

def _create_request() -> None:
    """Step 1: Generate the ECC keypair and create a key request email.

    Creates:
    - private_key.pem: Local ECC private key (saved for Step 3)
    - request.txt: Email message with the public key for contact
    """
    if _key_file.exists():
        print(f'Info: Key file {_key_file} already exists, skipping request creation.')
        return
    if _request_file.exists() and _private_key_file.exists():
        print(f'Info: Request file {_request_file} already exists, skipping request creation.')
        return
    private_key: EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP384R1())
    private_pem: bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key: EllipticCurvePublicKey = private_key.public_key()
    public_pem: str = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    _key_file.parent.mkdir(parents=True, exist_ok=True)
    _private_key_file.write_bytes(private_pem)
    request_email: str = (f'To: {contact}\n'
                          f'Subject: Key Request for {repo}\n\n'
                          f'Please encrypt and send the key file using the following public key:\n\n'
                          f'{public_pem}\n'
                          f'Thanks')
    _request_file.write_text(request_email)
    print(f'Request created at {_request_file}')
    print(f'Private key saved at {_private_key_file}')
    print(f'Please send the contents of {_request_file} to {contact}\n')


def _process_request() -> None:
    """Step 2: Encrypt the key file using requestor's public key.

    Reads:
    - request.txt: Requestor's public key
    - key.txt: Local encryption key to share

    Creates:
    - response.txt: Email with the encrypted key file
    """
    if not _key_file.exists():
        print(f'Error: Cannot process request, key file {_key_file} for {repo} not found.')
        return
    if not _request_file.exists():
        print(f'Error: Request file {_request_file} not found.')
        return
    request_content: str = _request_file.read_text()
    public_pem: str | None = _extract_pem_block(request_content, 'PUBLIC KEY')
    if public_pem is None:
        print('Error: Could not find public key in request file.')
        return
    public_key: EllipticCurvePublicKey = _decode_publickey(public_pem)
    ephemeral_private: EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP384R1())
    ephemeral_public: EllipticCurvePublicKey = ephemeral_private.public_key()
    ephemeral_public_pem: str = ephemeral_public.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    shared_key: bytes = _create_shared_key(ephemeral_private, public_key)
    key_content: bytes = _key_file.read_bytes()
    aad: bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    ciphertext: str = encrypt(key_content, key=shared_key, aad=aad).decode('utf-8')
    encrypted_lines: str = '\n'.join(ciphertext[i:i + 64] for i in range(0, len(ciphertext), 64))
    response_email: str = (f'To: [Requestor\'s email]\n'
                           f'Subject: Re: Key Request for {repo}\n\n'
                           f'Save the text contents of the email to {_key_file.parent.name}/{_response_file.name}\n\n'
                           f'{ephemeral_public_pem}\n'
                           f'-----BEGIN ENCRYPTED KEY-----\n'
                           f'{encrypted_lines}\n'
                           f'-----END ENCRYPTED KEY-----\n\n'
                           f'Thanks')
    _response_file.write_text(response_email)
    print(f'Response created at {_response_file}')
    print(f'Please send the contents of {_response_file} to the requestor\n')


def _process_response() -> None:
    """Step 3: Decrypt the received key file and clean up temporary files.

    Reads:
    - response.txt: Encrypted key file from contact
    - private_key.pem: Local private key from Step 1

    Creates:
    - key.txt: Decrypted encryption key

    Cleans up:
    - private_key.pem, request.txt, response.txt
    """
    if not _response_file.exists():
        print(f'Error: Nothing to do, response file {_response_file} not found.')
        return
    if not _private_key_file.exists():
        print(f'Error: Private key file {_private_key_file} not found.')
        return
    private_key: EllipticCurvePrivateKey = serialization.load_pem_private_key(_private_key_file.read_bytes(), None)
    response_content: str = _response_file.read_text()
    ephemeral_public_pem_data: str | None = _extract_pem_block(response_content, 'PUBLIC KEY')
    if ephemeral_public_pem_data is None:
        print('Error: Could not find ephemeral public key in response file.')
        return
    ciphertext: str | None = _extract_pem_block(response_content, 'ENCRYPTED KEY')
    if ciphertext is None:
        print('Error: Could not find encrypted key in response file.')
        return
    ephemeral_public_key: EllipticCurvePublicKey = _decode_publickey(ephemeral_public_pem_data)
    shared_key: bytes = _create_shared_key(private_key, ephemeral_public_key)
    aad: bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    try:
        key_content: bytes = decrypt(ciphertext.encode('utf-8'), key=shared_key, aad=aad)
    except Exception as e:
        print(f'Error: Decryption failed: {e}')
        return
    _key_file.write_bytes(key_content)
    print(f'Key file successfully created at {_key_file}')
    _private_key_file.unlink()
    _request_file.unlink(missing_ok=True)
    _response_file.unlink()
    print('Cleaned up temporary files.\n')


# ============================================================================
# Private Helpers - Key Management
# ============================================================================

@lru_cache()
def _get_key(*, key_file: Path = _key_file, key_size: int = _key_size, genkey: bool = False) -> bytes:
    """Get or generate the encryption key.

    Args:
        key_file: Path to the key file
        key_size: Size of the key in bytes
        genkey: Generate a new key if the file is not found

    Returns:
        SHA-256 hash of key file content
    """
    is_new_key: bool = False
    if not key_file.exists():
        if not genkey:
            if key_exchange() and key_file.exists():
                return _get_key(key_file=key_file)
            raise FileNotFoundError(
                f'Encryption key not found at {key_file.as_posix()}. '
                f'Contact the project maintainer for the encryption key.')
        new_key: str = '\n'.join(token_hex(key_size) for _ in range(16))
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key_file.write_text(new_key)
        print(f'Generated new encryption key and saved it to {key_file.as_posix()}')
        is_new_key = True
    else:
        print(f'Using existing encryption key from {key_file.as_posix()}')
    key: bytes = sha256(key_file.read_text().encode()).digest()
    _verify_key(key=key, is_new_key=is_new_key)
    return key


def _verify_key(*, key: bytes, is_new_key: bool = False) -> None:
    """Verify the encryption key by encrypting/decrypting test data.

    Args:
        key: Key to verify
        is_new_key: If True, generate new cipher text for verification

    Returns:
        None
    """
    # Plain text used to generate the cipher text using the default key
    # Pre-computed cipher text for the plain text using the default key
    # noinspection SpellCheckingInspection
    plain_text: bytes = (
        b'##############################################################\n'
        b'festival-ascertain-mouse-boasting-cherub-handcuff-hypocrisy-at\n'
        b'cdmtfzdq3kmmfkt5cdybspypgxfafrdt4xrs3iygz5pb7szitpfndyymx5mypf\n'
        b'unscathed-tubular-spectacle-mustang-staring-unheated-crimp-del\n'
        b'k4e4f4lamdptxsrrf6m7ijdte85emzre35fszk6ncmhagje3rex5kqkd63dp6y\n'
        b'##############################################################\n'
        b'######### First stanza from "Auguries of Innocence ##########"\n'
        b'##############################################################\n'
        b'To see a World in a Grain of Sand                             \n'
        b'And a Heaven in a Wild Flower;                                \n'
        b'Hold Infinity in the palm of your hand                        \n'
        b'And Eternity in an hour.                                      \n'
        b'                                        - William Blake (1803)\n'
        b'##############################################################\n'
        b'## Last stanza from "Stopping by Woods on a Snowy Evening" ###\n'
        b'##############################################################\n'
        b'The woods are lovely, dark and deep,                          \n'
        b'But I have promises to keep,                                  \n'
        b'And miles to go before I sleep,                               \n'
        b'And miles to go before I sleep.                               \n'
        b'                                         - Robert Frost (1923)\n'
        b'##############################################################\n'
        b'distort-overload-composite-humbly-shore-immovably-sanitizer-an\n'
        b'd9zsdisjdm9som6xkmczaxbnqglyfp3sskjhxzbgkdpmsga4gb6jypbqorkqa4\n'
        b'chump-talcum-wrangle-defeat-riptide-speller-undocked-hear-many\n'
        b'gggj9aphd3fmkyayqeqbxbjopsbgnxbjzrsz8igyccakxdngs4bja85ods9res\n'
        b'##############################################################\n'
    )
    # noinspection SpellCheckingInspection
    ciphertext: bytes = (
        rb'qO369KnBCxrlskDWgaEdqz5Ibng9yKpfLmU4vV3fjQZnd7m1yljVSlhbUA+0zxgW'
        rb'I3zPLUycFfey4ce4dOObZ02IFhzX/aunkb06NRd1z0oF+5L+qZHoISDkUAYsXGcl'
        rb'iqCzczbYgB0szxoVGJNsJUUWM71+0Z8O9lkM50kLSxXQGR2rbv9x/giMFaobZewb'
        rb'mqT6vU9WSiOtJsOPMV+wuywPp01yDL5FL4oy3yBHSgfSmgooy6y4q0PtwOBTv9RK'
        rb'x3sja2Lt1a17kRcqPjN9b444bQgSqbIL6M2P0SCqpmD+JOkAgpA74bmKI1n8XzW3'
        rb'4nWE08qCZ4VP7Ja1XDTfH1KLalEr3UCZ03Qe/QNqDsOk70cyhTx+AdLeOpEzo5XO'
        rb'wMV6lJRUNCRVy0yaTwLgmzONQMso8t3QMR3GWvdekya77/AAhOu/xOd0r21I3Slz'
        rb'Jfk59HT2GZIVj4LAITVKax8Bkmj/191hPZjRC1rUkkxBtjpUGNL4pVnZmolaxs1r'
        rb'w2Q8Sj6nCjRGpmZE+m148pIBr3zr4DpH/zf5EGmYOmQTP+wPqmlaN9FxF1Fys0LM'
        rb'39bFjEKmiANO6GUi/Pe+sbIenVCBTGY2NtSDblnpoelmLI0ryD9nvEEgFsS9ftaf'
        rb'ZGQHOvoMvJ+JDO2Zo3KKdh0oR3Wm4usoaiS2U0k3wKAA0Hrxg1L/9tm5Y+owliM9'
        rb'Wk0cG2CiKl1+Sfj0uKMYXpe6XlBjBf+IQuxGvBDLoF4VnDbgtvHGxR8tdPyVx+Ga'
        rb'zX+TJP8vzp7xDYWa4D2UvHbHjMRddBsbhVUN7gq5Cyuna0/3BNTECbJQ1hFYMf9J'
        rb'h52mLjmPD+r7Wh0WseHwSZIZa5C/9k8ttAGEdMlSd5sp9EPE837SdFX7Wcs/CTlr'
        rb'q6OH/SWd7wWzcnPhqBRzUQpvmgu+7SJcHLvg/45oBEd+IqBwvnDLtLbGayA/lDgi'
        rb'a405Tj1Lag976fg5Ablhi/aWsIZAKfNMrbHWRbYibsMD1aZAO1XqcP62KUDALWcp'
        rb'sL1SYq11B6BYnH9rZfWw952DYhwDeC7DjP6ss7VEj6eiDx9SvCujlpRV9alWvIh+'
        rb'PglxsfKZ5EppoBW/7EY8u3UC6S6MzQf/DPZi2EF165DtHAoj/m5veE4GegSBIE+k'
        rb'0YD/AOz+3IOPqpsn8lMdopwW73wYS+XBanaivb7EHD4oF6Y2YYSQd2w3j5n/Juam'
        rb'nwk3KQ+NLgNmwT87Q5dLlhq40+bu5X+VqzErKPdjmjRLlaLVtyGO05b5arcUfCrf'
        rb'zllx2qMrhQljE0sOMgybTYAjQ3ePjH2dZUL/vT+WUkxLlTAd9Fo5jksWsj2Iy9Hj'
        rb'DsUM088hRJiWMR3NWd6EuhEbF5YNtqt2nwubrqVTIfYYUE+unAHnmKGcy9g2t+Zv'
        rb'A89lZw8akrQi6Pi+0XnQi1qSA3h+eXdGn4R75Pftvq2oA/La2HGwJcIuvcilGi3z'
        rb'lcIsUySsgXMmLHNmt+k4IPStMoWVV28K6zMKnyrNLZUSeN1HYopLp82yFqt1eRnk'
        rb'mWz+ufOXUE++LNWnAG+sy/pZ30GXbtlUyAfDw4qQ9K0T+ZtkT0ooYvk1Dyp89vjH'
        rb'gLa+QxLFTe4PUr3JQ4vH17t71ty+NBPZVz1LwVdvQS1Qyuuq+voe+U9SNnzcLMBJ'
        rb'u6+z4bfc5rssIk7h8yHthVfBcO2XeU8bpjguTbKlZ3ASlidZlwNiiPRQqwxML0eo'
        rb'Oa+nuR+WTjcJK/0mg02UgNzb0s6aePVmYtoDEx7COIW9JP49PbTTsmibhlhnjR55'
        rb'OEFXPPmQXXtMT7AukBSIjlr6kmwRhyURGl+YMOddpqAk/UTcCiLwKwxQUuesB9f6'
        rb'71enjI4KzXODPlOKaGQqb3AcpFW0O08G6HDXuIrfg0pFyOPxHpnfAzATuHrdPcgy'
        rb'ziqHuBqj3oaF9Fze5S51fxq9PZSUywxnyqgXWeoduTeGKVw/rNyPnLj9Ey1yd5i2'
        rb'Vk5rTUSnhNiDESZlvPApLTaWPMVYvZZV3zOVi4GXhdDEljVbtJ1FIJuO4GBTE+ml'
        rb'tO98dCOn75DjbJRuHFJUcMkuZ414t100czvRDvl3tHb018a2l13WKajgtydEh07i'
        rb'R4gtCAY6R3xhFBc0PxDpjGZgz4l1PRl30oYSqJfaBAIuDpJgD7hFI0VJ/JPfbDAJ'
        rb'0Mr4mRvgnx3KvhSubXT24n6yL742z6tIbyXByafLvsVzuIVYMiGEmDDDmaHDUTZ8'
        rb'EfYSCp2R/xNn5KSN+ldwuWR2C9SnBoEOBXjdVZxr1WvaYubjyE7rPtmKARx8BBo2'
        rb'SA=='
    )
    if is_new_key:
        ciphertext: bytes = encrypt(plain_text, key=key)
        print('New cipher text:')
        cipher_text_str: str = ciphertext.decode()
        print('\n'.join(f"rb'{cipher_text_str[i:i + 64]}'" for i in range(0, len(cipher_text_str), 64)))
    try:
        assert decrypt(ciphertext, key=key) == plain_text, 'decrypted text does not match original text'
    except Exception as e:
        print(f'Error verifying key: {e}')
        print(f'Error: verifying key, please contact the project maintainer at {repo} for the encryption key.')
        raise


# ============================================================================
# Main Entry Point
# ============================================================================

def vault_main(mode: Literal['user', 'process', 'new', 'verify']) -> None:
    """Main cli entry point for vault operations.

    Args:
        mode: Operation mode
            - 'user': End-user flow (auto key exchange if needed)
            - 'process': Contact flow (process incoming request)
            - 'new': Generate a new encryption key
            - 'verify': Run integration test

    Usage:
        python solver/vault.py user
        python solver/vault.py process
        python solver/vault.py new
        python solver/vault.py verify
    """
    if mode == 'user':
        key_exchange()
        if _key_file.exists():
            _verify_key(key=_get_key(genkey=False))
    elif mode == 'process':
        _process_request()
    elif mode == 'new':
        _verify_key(key=_get_key(genkey=True), is_new_key=True)
    elif mode == 'verify':
        _verify_key(key=_get_key())
        temp_key_file: Path = _key_file.with_suffix('.tmp')
        _key_file.rename(temp_key_file)
        key_exchange()
        assert _private_key_file.exists()
        assert _request_file.exists()
        temp_key_file.rename(_key_file)
        _process_request()
        assert _response_file.exists()
        _key_file.rename(temp_key_file)
        key_exchange()
        if not _key_file.exists():
            temp_key_file.rename(_key_file)
            _private_key_file.unlink(missing_ok=True)
            _request_file.unlink(missing_ok=True)
            _response_file.unlink(missing_ok=True)
            print('Error: Key file not found after key exchange.')
        else:
            temp_key_file.unlink()
            _verify_key(key=_get_key())


if __name__ == '__main__':
    from sys import argv

    raise SystemExit(vault_main(argv[1] if len(argv) > 1 else 'user'))
