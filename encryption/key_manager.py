
import os
import base64


def load_key(environment_variable):

    encoded = os.getenv(environment_variable)

    if not encoded:
        raise RuntimeError(
            f"Missing environment variable: {environment_variable}"
        )

    try:

        key = base64.b64decode(
            encoded,
            altchars=b"-_",
            validate=True
        )

    except Exception as exc:

        raise RuntimeError(
            f"{environment_variable} must be a valid URL-safe Base64 key."
        ) from exc

    if len(key) != 32:

        raise RuntimeError(
            f"{environment_variable} must decode to exactly 32 bytes."
        )

    return key


def load_encryption_key():

    return load_key("VAULTEX_ENCRYPTION_KEY")


def load_integrity_key():

    return load_key("VAULTEX_INTEGRITY_KEY")
