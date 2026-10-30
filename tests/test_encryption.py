
import io

import pytest

from encryption.aes_encryption import (
    encrypt_file,
    decrypt_file,
    encrypt_file_chunks,
    decrypt_file_chunks
)


TEST_KEY = b"0123456789abcdef0123456789abcdef"


def test_encrypt_and_decrypt():

    original = b"VAULTEX secure file transfer"

    nonce, encrypted = encrypt_file(
        original,
        TEST_KEY
    )

    decrypted = decrypt_file(
        nonce,
        encrypted,
        TEST_KEY
    )

    assert decrypted == original


def test_wrong_key_fails():

    original = b"Private file contents"

    nonce, encrypted = encrypt_file(
        original,
        TEST_KEY
    )

    wrong_key = b"abcdef0123456789abcdef0123456789"

    with pytest.raises(Exception):

        decrypt_file(
            nonce,
            encrypted,
            wrong_key
        )


def test_chunk_encryption_and_decryption():

    original = b"A" * 5000

    source = io.BytesIO(original)

    encrypted_output = io.BytesIO()

    encrypt_file_chunks(
        source,
        encrypted_output,
        TEST_KEY,
        chunk_size=1024
    )

    encrypted_output.seek(0)

    decrypted_output = io.BytesIO()

    decrypt_file_chunks(
        encrypted_output,
        decrypted_output,
        TEST_KEY
    )

    assert decrypted_output.getvalue() == original


def test_empty_file():

    source = io.BytesIO(b"")

    encrypted_output = io.BytesIO()

    encrypt_file_chunks(
        source,
        encrypted_output,
        TEST_KEY,
        chunk_size=1024
    )

    encrypted_output.seek(0)

    decrypted_output = io.BytesIO()

    decrypt_file_chunks(
        encrypted_output,
        decrypted_output,
        TEST_KEY
    )

    assert decrypted_output.getvalue() == b""


def test_corrupted_encrypted_file_fails():

    source = io.BytesIO(b"Important data")

    encrypted_output = io.BytesIO()

    encrypt_file_chunks(
        source,
        encrypted_output,
        TEST_KEY,
        chunk_size=1024
    )

    corrupted = bytearray(
        encrypted_output.getvalue()
    )

    corrupted[-1] ^= 1

    with pytest.raises(Exception):

        decrypt_file_chunks(
            io.BytesIO(bytes(corrupted)),
            io.BytesIO(),
            TEST_KEY
        )
