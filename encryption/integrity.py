
import hashlib
import hmac

from encryption.key_manager import load_integrity_key


def generate_hmac(file_data, integrity_key=None):

    if not isinstance(file_data, bytes):
        raise TypeError("File data must be bytes.")

    key = integrity_key or load_integrity_key()

    if not isinstance(key, bytes) or len(key) != 32:
        raise ValueError(
            "HMAC key must be exactly 32 bytes."
        )

    signature = hmac.new(
        key,
        file_data,
        hashlib.sha256
    ).hexdigest()

    return signature


def verify_hmac(
    file_data,
    integrity_key,
    original_signature
):

    if not original_signature:
        raise ValueError(
            "Original HMAC signature is required."
        )

    return hmac.compare_digest(
        generate_hmac(file_data, integrity_key),
        original_signature
    )
