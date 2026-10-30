
import os
import hmac
import hashlib
import tempfile

from pathlib import Path

from flask import (
    Blueprint,
    abort,
    send_file,
    current_app
)

from flask_login import login_required, current_user

from config import Config

from database.database import get_file_by_id_and_user

from encryption.aes_encryption import decrypt_file_chunks

from encryption.key_manager import (
    load_encryption_key,
    load_integrity_key
)


download_bp = Blueprint("download", __name__)


def calculate_file_hmac(file_path, key):

    digest = hmac.new(
        key,
        digestmod=hashlib.sha256
    )

    with open(file_path, "rb") as stream:

        for block in iter(
            lambda: stream.read(Config.CHUNK_SIZE),
            b""
        ):

            digest.update(block)

    return digest.hexdigest()


@download_bp.route(
    "/download/<int:file_id>",
    methods=["GET"]
)
@login_required
def download_file(file_id):

    plaintext_path = None
    fd = None

    try:

        # Find the file belonging to the current user

        record = get_file_by_id_and_user(
            file_id,
            int(current_user.id)
        )

        if record is None:
            abort(404)

        # Validate the encrypted storage path

        storage = Path(
            Config.STORAGE_FOLDER
        ).resolve()

        stored_name = record["stored_filename"]

        if Path(stored_name).name != stored_name:
            abort(404)

        encrypted_path = (
            storage / stored_name
        ).resolve()

        if (
            encrypted_path.parent != storage
            or not encrypted_path.is_file()
        ):
            abort(404)

        # Load private security keys

        integrity_key = load_integrity_key()

        encryption_key = load_encryption_key()

        # Verify encrypted file integrity

        actual = calculate_file_hmac(
            encrypted_path,
            integrity_key
        )

        if not hmac.compare_digest(
            actual,
            record["integrity_hash"]
        ):

            current_app.logger.error(
                "Integrity check failed for file ID %s",
                file_id
            )

            abort(500)

        # Create a temporary file for decrypted content

        fd, temp_name = tempfile.mkstemp(
            suffix=".tmp"
        )

        plaintext_path = Path(temp_name)

        with os.fdopen(fd, "wb") as output:

            fd = None

            with open(
                encrypted_path,
                "rb"
            ) as source:

                decrypt_file_chunks(
                    source,
                    output,
                    encryption_key
                )

            output.flush()

            os.fsync(
                output.fileno()
            )

        # Send the decrypted file to the user

        response = send_file(
            plaintext_path,
            as_attachment=True,
            download_name=record["original_filename"],
            mimetype="application/octet-stream",
            conditional=False
        )

        cleanup_path = plaintext_path

        response.call_on_close(
            lambda path=cleanup_path:
            path.unlink(missing_ok=True)
        )

        plaintext_path = None

        return response

    except Exception as error:

        if fd is not None:
            os.close(fd)

        if plaintext_path and plaintext_path.exists():

            plaintext_path.unlink(
                missing_ok=True
            )

        if getattr(error, "code", None) == 404:
            raise

        current_app.logger.exception(
            "Download failed for file ID %s",
            file_id
        )

        abort(
            500,
            description="The secure download could not be completed."
        )
