
"""Generate fresh VAULTEX secrets for the private .env file.

Do not share these values or commit them to GitHub.
"""

import base64
import secrets


# Generate Flask application secret
flask_secret = secrets.token_urlsafe(48)


# Generate AES-256 encryption key
encryption_key = base64.urlsafe_b64encode(
    secrets.token_bytes(32)
).decode()


# Generate a separate HMAC integrity key
integrity_key = base64.urlsafe_b64encode(
    secrets.token_bytes(32)
).decode()


print("FLASK_SECRET_KEY=" + flask_secret)
print("VAULTEX_ENCRYPTION_KEY=" + encryption_key)
print("VAULTEX_INTEGRITY_KEY=" + integrity_key)
