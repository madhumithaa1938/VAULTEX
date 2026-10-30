
import pytest

from encryption.integrity import (
    generate_hmac,
    verify_hmac
)


TEST_KEY = b"0123456789abcdef0123456789abcdef"


def test_generate_hmac():

    file_data = b"VAULTEX secure file"

    signature = generate_hmac(
        file_data,
        TEST_KEY
    )

    assert isinstance(signature, str)

    assert len(signature) == 64


def test_valid_integrity():

    file_data = b"Important private data"

    signature = generate_hmac(
        file_data,
        TEST_KEY
    )

    result = verify_hmac(
        file_data,
        TEST_KEY,
        signature
    )

    assert result is True


def test_modified_file_fails():

    original_data = b"Original file contents"

    signature = generate_hmac(
        original_data,
        TEST_KEY
    )

    modified_data = b"Modified file contents"

    result = verify_hmac(
        modified_data,
        TEST_KEY,
        signature
    )

    assert result is False


def test_wrong_key_fails():

    file_data = b"Secure information"

    signature = generate_hmac(
        file_data,
        TEST_KEY
    )

    wrong_key = b"abcdef0123456789abcdef0123456789"

    result = verify_hmac(
        file_data,
        wrong_key,
        signature
    )

    assert result is False


def test_missing_signature_fails():

    with pytest.raises(ValueError):

        verify_hmac(
            b"Some data",
            TEST_KEY,
            ""
        )
