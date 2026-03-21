#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""AES encryption and decryption for sensitive problem data."""
from __future__ import annotations

from base64 import b64decode, b64encode
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from secrets import token_hex

import Crypto  # pip install pycryptodome
import Crypto.Cipher.AES
import Crypto.Hash.SHA256
import Crypto.Util.Padding

__all__ = ['encrypt', 'decrypt']

# ============================================================================
# Constants
# ============================================================================

# File paths and key size
KEY_FILE: Path = Path.cwd() / 'keys' / 'key.txt'  # Main encryption key file
KEY_SIZE: int = 32  # AES-256 requires 32 bytes (256 bits)
REPO: str = 'https://github.com/vikasmunshi/euler'


# ============================================================================
# Encryption/Decryption Functions
# ============================================================================

def decrypt(cypher_text: bytes, *, key: bytes = None) -> bytes:
    """Decrypt AES-256 encrypted data.

    Args:
        cypher_text: Base64-encoded encrypted data
        key: Encryption key (uses default if not provided)

    Returns:
        Decrypted plaintext bytes
    """
    key = key or _get_key()
    decoded_cypher_text = b64decode(cypher_text)
    iv = decoded_cypher_text[:Crypto.Cipher.AES.block_size]
    cipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv=iv)
    plain_text = cipher.decrypt(decoded_cypher_text[Crypto.Cipher.AES.block_size:])
    return Crypto.Util.Padding.unpad(plain_text, Crypto.Cipher.AES.block_size)


def encrypt(plain_text: bytes, *, key: bytes = None) -> bytes:
    """Encrypt data using AES-256.

    Args:
        plain_text: Data to encrypt
        key: Encryption key (uses default if not provided)

    Returns:
        Base64-encoded encrypted data
    """
    key = key or _get_key()
    cipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC)
    cipher_text = cipher.encrypt(Crypto.Util.Padding.pad(plain_text, Crypto.Cipher.AES.block_size))
    return b64encode(cipher.iv + cipher_text)


# ============================================================================
# Key Management (Private)
# ============================================================================

@lru_cache()
def _get_key(*, key_file: Path = KEY_FILE, key_size: int = KEY_SIZE, genkey: bool = False) -> bytes:
    """Get or generate the encryption key.

    Args:
        key_file: Path to the key file
        key_size: Size of the key in bytes
        genkey: Generate a new key if the file is not found

    Returns:
        SHA-256 hash of key file content
    """
    if not key_file.exists():
        if not genkey:
            raise FileNotFoundError(
                f'Encryption key not found at {key_file.as_posix()}. '
                f'Contact the project maintainer for the encryption key.')
        new_key: str = '\n'.join(token_hex(key_size) for _ in range(16))
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key_file.write_text(new_key)
        print(f'Generated new encryption key and saved it to {key_file.as_posix()}')
        _verify_key(key=sha256(new_key.encode()).digest(), is_new_key=True)
    else:
        print(f'Using existing encryption key from {key_file.as_posix()}')
    key: bytes = sha256(key_file.read_text().encode()).digest()
    _verify_key(key=key, is_new_key=False)
    return key


def _verify_key(*, key: bytes, is_new_key: bool = False) -> None:
    """Verify the encryption key by encrypting/decrypting test data.

    Args:
        key: Key to verify
        is_new_key: If True, generate new cipher text for verification

    Returns:
        None
    """
    # Plain text used to generate the cipher text suing the default key
    # Pre-computed cipher text for the above plain text using the default key
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
        b'And a Heaven in a Wild Flower,                                \n'
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
    cipher_text: bytes = (
        rb'Npiys6KF7MHU8Ac/gF/IY4mnVfh4EZoI3eI1M07ma5hm6hzT2g1j8X2ILUrCNTak'
        rb'Sq6e6GO7SsKy0uz+jp8jdzRCRA9aqx5AGcmQAbs4GVoH6deGmq78SyL5PNI6P/a8'
        rb'3gWF7FHHdKR6cvXqPAUOSrx624Al5Y9/RB4/9j9LNyHBecbb8Jl7FPVZ83a36yyq'
        rb'o2dpzx53c6B5TBHTk9xEHyQ3pbpfq4gj5AZVWVVDL6vEuPeuURPBTeVvku1W5K4B'
        rb'QYtTX7jvmeGfuCTOkoneKQTPddALewiYl1YYSzWZP6gg7JD2n/hB00R70y9q5i+R'
        rb'ZjJzTjBm6El5HXioNj+kU5NHGCIZE09CRZT58EnUJRdRLMJk51lvHdIMrMknPQmX'
        rb'ImGQCzmLmHK9gokTFWLmH4sp4OunwEOgXWbEhLezUgF4+eT6X+5/dAGPbIbO7Fwh'
        rb'VaREya+tPwM3Z1yXREjMEoBNXD+cju8/LmtJjMls+YMLX75sa2UcHSUJGN1+NOTe'
        rb'zrigik4f+/AV8olsHEfpiccT7Mxd3Vqc6odHRAQ7RJufk8tQD55+Org7iFM/xkg6'
        rb'rdx/q/aIxV9k3CDt0z+vDCXYgC0rRjnl53HcqRL+hVSpDNyu36x1AknHiHReSPap'
        rb'oA9Uicp60+/xFH/vPQOjeZJ9EcvbkYGolxqZpJpyEpbQmpePJK1BHN1IGrGmama9'
        rb'z8QC6neCu0SppmKfNQaIppEieysqAU4E9iO5ZCoyacjF56y2ylR50tHq+KmvdBPj'
        rb'OQYqbPXC/F1aorG2fWRXs8AqXlvsYZtFZFpAQGrbYzRvWUNwzVEBLKfb8BHZMFfA'
        rb'2MW3TyKSqKtpwgYCoVukE7gMLyLR7NeVF5jJxenGUILMGt23748jizXQ6vinDRdt'
        rb'4c1+W7FhRF9HxuCAB41r4ap1x+3rPOUyehZUH5AGSBIjSzQzFINts482yZCYsTAi'
        rb'UjIKHGDNVIyW7J0gBP1lZT+gN/Z9gxH/7/1bHT14U6Eg622TiXWt/mUEL8h7GBGj'
        rb'CNv7rSIJS1/lxnHrUiV7XOelKwuNhX/XJG28tSeUiB56jx+2f1YTqTnTmPOHIiea'
        rb'W3U5S8OMkuVf93giDJXHiEEdBiJFIYKdlU8QO1fJqWuO6jJv2AZG7EvBG/qkGf+P'
        rb'D+I1iYy6DnFS7AIkC3EHZYvQ3POnbk8f2lC29DNdxMcJDvWNSRE4Bx+N/qwagvuB'
        rb'bZ6e4GGGSG6AzwVC8CRYoFNWbJ6e6SQqLX40Scs43Jw2VlleuLWrfC9UXDoUGqUD'
        rb'33azGCGXYYRjkSwJ+1YjDyCcerq/7d5zL+kiMqKwW6Ddh+pvvIsQS5cv/DErFUNU'
        rb'OFx1N5qFlejVXWYN3gr5zD/Foils3P5QaMSy95+maDrtBIByUJnBHhMrF5utJqTY'
        rb'0z61oB6i/jZIkaRVkiICBLf37YgFINlPB4e1A7wNrfq14cmCjYRatlEWYXaGOtdR'
        rb'9mKIH5RDk9DC/RWthHynviIx21uXVKDeK6bvXWQe3mz2fGJA1FZrAc76jkwXr8Hg'
        rb'8Xq1nfdO6smZFagQhX8i5W6f9Yb7yLqC3jOCXKug66IhR8TY+vlEKwDsM0NLvZEQ'
        rb'1OvRLWtlWyfkYxUHZyrI8/u2MxvrF0RZzapfy9m864e3p7DX0zl32A7573y02aA7'
        rb'ExvpA4fOchyibUZQ91YdqhMexjUNHzr1//xM1v7qsge0h7BwVoZvCxKRdNNVGdJs'
        rb'hAYd/c8yGK4NtTBDNTVhVjYqqs+BF+W0kALu+1O7AlKCPlkkel8cv/hxWMUdLCMj'
        rb'ah7wV8uL9NZmIikJSKMklTj4mo4l4fT2cKHP5Zuv8FIAh97CXc7y0jflFdy/vkWz'
        rb'98O7qdGAbCB9H1yMafVMnsdYfQp/NifKwlaeez9ncytNBc/U6hEzf0fE1vqTMJ5P'
        rb'qJSaCVHHGoVukZhjVEE7adNIS7CRLPL4teZqj0c6t1Rq6wQfPvFptMpb3Z7ocI8m'
        rb'PKlfdKZqv4vzDR+1bF+pCX8A/Xyp7hTyZKGhNvRT5dVjHWRQreocCnT3gOlEp5Wt'
        rb'ZodCxYOL72WtNvm8eJHViopeo6W67Fl8xi155g4VPfr7URVr4+anFAorg764EWZK'
        rb'7p1db0tstclio/F588RIXlUbaRJouYjsEh0D38eAWxw5EYLoqdfrrNPbMP4Htt3I'
        rb'EOFnQ9s99yne6Ex5gm2nTjELoGgXYgfnrKKvOWohq2bO7fkk1hxu7MPevslBIieg'
        rb'IXy4iIkadUi8/JaRic17LhauafIqxImL1Rt0yzSs7Oj5AvjhikZpAuF1v52WCi+8'
    )
    if is_new_key:
        cipher_text = encrypt(plain_text, key=key)
        print('New cipher text:')
        _print_cipher_text(cipher_text)
    try:
        assert decrypt(cipher_text, key=key) == plain_text
    except Exception as e:
        print(f'Error verifying key: {e}')
        cipher_text = encrypt(plain_text, key=key)
        print('Possible cipher text:')
        _print_cipher_text(cipher_text)
        print(f'\nError: please contact the project maintainer at {REPO} for the encryption key.')
        raise


def _print_cipher_text(cipher_text: bytes) -> None:
    """Prints the cipher text in a readable format."""
    cipher_text_str: str = cipher_text.decode()
    cipher_text_len: int = len(cipher_text_str)
    for line_len in range(60, 100):
        if cipher_text_len % line_len == 0:
            print('\n'.join(f"rb'{cipher_text_str[i:i + line_len]}'" for i in range(0, cipher_text_len, line_len)))
            break


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    # _ = _get_key(genkey=True)
    raise SystemExit(0 if _verify_key(key=_get_key(genkey=True), is_new_key=False) else 1)
