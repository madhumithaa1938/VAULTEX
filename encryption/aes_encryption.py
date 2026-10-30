
import os
import struct

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import Config
from encryption.key_manager import load_encryption_key


MAGIC = b"VLTENC02"

HEADER_SIZE = 12
TAG_SIZE = 16

DEFAULT_CHUNK_SIZE = 1024 * 1024
MAX_CHUNK_SIZE = 4 * 1024 * 1024


def validate_key(key):

    if not isinstance(key, bytes) or len(key) != 32:
        raise ValueError(
            "AES-256-GCM requires a 32-byte key."
        )


def generate_key():

    return AESGCM.generate_key(bit_length=256)


def encrypt_file(file_data, key=None):

    if not isinstance(file_data, bytes):
        raise TypeError("File data must be bytes.")

    key = key or load_encryption_key()

    validate_key(key)

    nonce = os.urandom(12)

    encrypted_data = AESGCM(key).encrypt(
        nonce,
        file_data,
        None
    )

    return nonce, encrypted_data


def decrypt_file(nonce, encrypted_data, key=None):

    key = key or load_encryption_key()

    validate_key(key)

    if not isinstance(nonce, bytes) or len(nonce) != 12:
        raise ValueError("AES-GCM nonce must be 12 bytes.")

    return AESGCM(key).decrypt(
        nonce,
        encrypted_data,
        None
    )


def _read_exact(stream, length):

    data = stream.read(length)

    if len(data) != length:
        raise ValueError(
            "Encrypted file is truncated or corrupted."
        )

    return data


def encrypt_file_chunks(
    input_file,
    output_file,
    key=None,
    chunk_size=None
):

    key = key or load_encryption_key()

    validate_key(key)

    chunk_size = chunk_size or Config.CHUNK_SIZE

    if (
        not isinstance(chunk_size, int)
        or not 1 <= chunk_size <= MAX_CHUNK_SIZE
    ):

        raise ValueError("Invalid chunk size.")

    header = MAGIC + struct.pack(">I", chunk_size)

    output_file.write(header)

    aesgcm = AESGCM(key)

    counter = 0

    while True:

        chunk = input_file.read(chunk_size)

        if not chunk:
            break

        if counter >= 0xFFFFFFFF:
            raise ValueError("File contains too many chunks.")

        nonce = os.urandom(12)

        aad = (
            header
            + b"CHNK"
            + counter.to_bytes(8, "big")
            + len(chunk).to_bytes(4, "big")
        )

        encrypted = aesgcm.encrypt(
            nonce,
            chunk,
            aad
        )

        output_file.write(
            struct.pack(">I", len(chunk))
        )

        output_file.write(nonce)

        output_file.write(encrypted)

        counter += 1

    # Authenticated end marker prevents silent truncation.

    final_nonce = os.urandom(12)

    final_aad = (
        header
        + b"FINAL"
        + counter.to_bytes(8, "big")
    )

    final_tag = aesgcm.encrypt(
        final_nonce,
        b"",
        final_aad
    )

    output_file.write(struct.pack(">I", 0))

    output_file.write(final_nonce)

    output_file.write(final_tag)


def decrypt_file_chunks(
    input_file,
    output_file,
    key=None
):

    key = key or load_encryption_key()

    validate_key(key)

    magic = _read_exact(input_file, 8)

    if magic != MAGIC:
        raise ValueError(
            "Not a supported VAULTEX encrypted file."
        )

    chunk_size_bytes = _read_exact(input_file, 4)

    chunk_size = struct.unpack(
        ">I",
        chunk_size_bytes
    )[0]

    if not 1 <= chunk_size <= MAX_CHUNK_SIZE:
        raise ValueError("Invalid encrypted chunk size.")

    header = magic + chunk_size_bytes

    aesgcm = AESGCM(key)

    counter = 0

    while True:

        length = struct.unpack(
            ">I",
            _read_exact(input_file, 4)
        )[0]

        nonce = _read_exact(input_file, 12)

        # Authenticated end marker

        if length == 0:

            final_tag = _read_exact(
                input_file,
                TAG_SIZE
            )

            final_aad = (
                header
                + b"FINAL"
                + counter.to_bytes(8, "big")
            )

            aesgcm.decrypt(
                nonce,
                final_tag,
                final_aad
            )

            if input_file.read(1):
                raise ValueError(
                    "Unexpected trailing data."
                )

            return

        if length > chunk_size:
            raise ValueError(
                "Invalid encrypted chunk length."
            )

        encrypted = _read_exact(
            input_file,
            length + TAG_SIZE
        )

        aad = (
            header
            + b"CHNK"
            + counter.to_bytes(8, "big")
            + length.to_bytes(4, "big")
        )

        plaintext = aesgcm.decrypt(
            nonce,
            encrypted,
            aad
        )

        output_file.write(plaintext)

        counter += 1
