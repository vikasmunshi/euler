#!/usr/bin/env python3.14
from __future__ import annotations

from base64 import b64decode, b64encode
from secrets import token_bytes

from cryptography.hazmat.primitives import hashes, serialization  # pip install cryptography
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, EllipticCurvePublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from solver.vault import KEY_FILE, REPO

PRIVATE_KEY_FILE = KEY_FILE.parent / 'private_key.pem'
REQUEST_FILE = KEY_FILE.parent / 'request.txt'
RESPONSE_FILE = KEY_FILE.parent / 'response.txt'
CONTACT: str = 'vikas.munshi@gmail.com'


def _extract_pem_block(content: str, marker: str) -> str | None:
    start_marker = f'-----BEGIN {marker}-----'
    end_marker = f'-----END {marker}-----'
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    if start_idx == -1 or end_idx == -1:
        return None
    return content[start_idx + len(start_marker):end_idx].strip()


def _load_public_key_from_pem(pem_data: str) -> EllipticCurvePublicKey:
    pem_full = f'-----BEGIN PUBLIC KEY-----\n{pem_data}\n-----END PUBLIC KEY-----'
    return serialization.load_pem_public_key(pem_full.encode('utf-8'))


def _create_aesgcm(private_key, public_key) -> AESGCM:
    shared_key = private_key.exchange(ec.ECDH(), public_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'key-exchange'
    ).derive(shared_key)
    return AESGCM(derived_key)


def create_request() -> None:
    if KEY_FILE.exists():
        print(f'Info: Key file {KEY_FILE} already exists, skipping request creation.')
        return
    if REQUEST_FILE.exists():
        print(f'Info: Request file {REQUEST_FILE} already exists, skipping request creation.')
        return
    private_key: EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP384R1())
    public_key: EllipticCurvePublicKey = private_key.public_key()
    public_pem: str = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    private_pem: bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    PRIVATE_KEY_FILE.write_bytes(private_pem)
    request_email: str = (f'To: {CONTACT}\n'
                          f'Subject: Key Request for {REPO}\n\n'
                          f'Please encrypt and send the key file using the following public key:\n\n'
                          f'{public_pem}\n'
                          f'Thanks')
    REQUEST_FILE.write_text(request_email)
    print(f'Request created at {REQUEST_FILE}')
    print(f'Private key saved at {PRIVATE_KEY_FILE}')
    print(f'Please send the contents of {REQUEST_FILE} to {CONTACT}\n')


def process_request() -> None:
    if not KEY_FILE.exists():
        print(f'Error: Cannot process request, key file {KEY_FILE} for {REPO} not found.')
        return
    if not REQUEST_FILE.exists():
        print(f'Error: Request file {REQUEST_FILE} not found.')
        return
    request_content: str = REQUEST_FILE.read_text()
    public_key_pem_data: str | None = _extract_pem_block(request_content, 'PUBLIC KEY')
    if public_key_pem_data is None:
        print('Error: Could not find public key in request file.')
        return
    public_key: EllipticCurvePublicKey = _load_public_key_from_pem(public_key_pem_data)
    ephemeral_private: EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP384R1())
    ephemeral_public: EllipticCurvePublicKey = ephemeral_private.public_key()
    aesgcm: AESGCM = _create_aesgcm(ephemeral_private, public_key)
    key_content: bytes = KEY_FILE.read_bytes()
    nonce: bytes = token_bytes(12)
    ciphertext: bytes = aesgcm.encrypt(nonce, key_content, None)
    ephemeral_public_pem: str = ephemeral_public.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    combined: bytes = nonce + ciphertext
    combined_b64: str = b64encode(combined).decode('utf-8')
    encrypted_lines: str = '\n'.join(combined_b64[i:i + 64] for i in range(0, len(combined_b64), 64))
    response_email: str = (f'To: [Requestor\'s email]\n'
                           f'Subject: Re: Key Request for {REPO}\n\n'
                           f'Save the text contents of the email to {KEY_FILE.parent.name}/{RESPONSE_FILE.name}\n'
                           f'Here is the encrypted key file:\n\n'
                           f'{ephemeral_public_pem}\n'
                           f'-----BEGIN ENCRYPTED KEY-----\n'
                           f'{encrypted_lines}\n'
                           f'-----END ENCRYPTED KEY-----\n\n'
                           f'Thanks')
    RESPONSE_FILE.write_text(response_email)
    print(f'Response created at {RESPONSE_FILE}')
    print(f'Please send the contents of {RESPONSE_FILE} to the requestor\n')


def process_response() -> None:
    if not RESPONSE_FILE.exists():
        print(f'Error: Nothing to do, response file {RESPONSE_FILE} not found.')
        return
    if not PRIVATE_KEY_FILE.exists():
        print(f'Error: Private key file {PRIVATE_KEY_FILE} not found.')
        return
    if KEY_FILE.exists():
        print(f'Warning: Key file {KEY_FILE} already exists and will be overwritten.')
        response = input('Continue? (y/n): ')
        if response.lower() != 'y':
            return
    private_key: EllipticCurvePrivateKey = serialization.load_pem_private_key(PRIVATE_KEY_FILE.read_bytes(),
                                                                              password=None)
    response_content: str = RESPONSE_FILE.read_text()
    ephemeral_public_pem_data: str | None = _extract_pem_block(response_content, 'PUBLIC KEY')
    if ephemeral_public_pem_data is None:
        print('Error: Could not find ephemeral public key in response file.')
        return
    ephemeral_public_key: EllipticCurvePublicKey = _load_public_key_from_pem(ephemeral_public_pem_data)
    combined_b64: str | None = _extract_pem_block(response_content, 'ENCRYPTED KEY')
    if combined_b64 is None:
        print('Error: Could not find encrypted key in response file.')
        return
    combined_b64 = combined_b64.replace('\n', '').replace('\r', '').replace(' ', '')
    combined: bytes = b64decode(combined_b64)
    nonce: bytes = combined[:12]
    ciphertext: bytes = combined[12:]
    aesgcm: AESGCM = _create_aesgcm(private_key, ephemeral_public_key)
    try:
        plaintext: bytes = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        print(f'Error: Decryption failed: {e}')
        return
    KEY_FILE.write_bytes(plaintext)
    print(f'Key file successfully created at {KEY_FILE}')
    PRIVATE_KEY_FILE.unlink()
    REQUEST_FILE.unlink()
    RESPONSE_FILE.unlink()
    print('Cleaned up temporary files.\n')


def test():
    key_file_name: str = KEY_FILE.name
    key_file_path = KEY_FILE.parent / key_file_name
    backup_key_file_path = KEY_FILE.parent / 'backup.txt'
    PRIVATE_KEY_FILE.unlink(missing_ok=True)
    REQUEST_FILE.unlink(missing_ok=True)
    RESPONSE_FILE.unlink(missing_ok=True)
    print('Running tests...')
    key_file_path.rename(backup_key_file_path)
    print(f'Key file renamed to {backup_key_file_path} for testing purposes.')
    assert not key_file_path.exists()
    print('Creating request...')
    create_request()
    print('Processing request...')
    key_file_path.write_bytes(backup_key_file_path.read_bytes())
    print(f'Key file restored from backup at {key_file_path}')
    process_request()
    print('Processing response...')
    key_file_path.unlink()
    print(f'Key file deleted at {key_file_path}')
    assert not key_file_path.exists()
    process_response()
    assert key_file_path.exists()
    assert key_file_path.read_bytes() == backup_key_file_path.read_bytes()
    print('All tests passed successfully.')


if __name__ == '__main__':
    raise SystemExit(test())
