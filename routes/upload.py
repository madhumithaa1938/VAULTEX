
import os
import uuid
import hmac
import hashlib
import tempfile

from pathlib import Path

from flask import (
    Blueprint,
    request,
    render_template,
    flash,
    redirect,
    url_for,
    current_app
)

from flask_login import login_required, current_user

from werkzeug.utils import secure_filename

from config import Config

from database.database import create_file_record

from encryption.aes_encryption import encrypt_file_chunks

from encryption.key_manager import load_integrity_key


upload_bp = Blueprint("upload", __name__)


def allowed_file(filename):

    return bool(
        filename
        and "."
        in filename
        and filename.rsplit(".", 1)[1].lower()
        in Config.ALLOWED_EXTENSIONS
    )


def calculate_file_hmac(file_path, integrity_key):

    digest = hmac.new(
        integrity_key,
        digestmod=hashlib.sha256
    )

    with open(file_path, "rb") as stream:

        for block in iter(
            lambda: stream.read(Config.CHUNK_SIZE),
            b""
        ):

            digest.update(block)

    return digest.hexdigest()


@upload_bp.route("/upload", methods=["GET"])
@login_required
def upload_page():

    return render_template("upload.html")


@upload_bp.route("/upload", methods=["POST"])
@login_required
def upload_file():

    temporary_path = None
    final_path = None

    try:

        uploaded = request.files.get("file")

        if uploaded is None or not uploaded.filename:

            flash(
                "Choose a file before uploading.",
                "error"
            )

            return redirect(
                url_for("upload.upload_page")
            )

        filename = secure_filename(
            uploaded.filename
        )

        if not filename or not allowed_file(filename):

            flash(
                "This file type is not supported.",
                "error"
            )

            return redirect(
                url_for("upload.upload_page")
            )

        uploaded.stream.seek(0, os.SEEK_END)

        size = uploaded.stream.tell()

        uploaded.stream.seek(0)

        if size == 0:

            flash(
                "Empty files cannot be uploaded.",
                "error"
            )

            return redirect(
                url_for("upload.upload_page")
            )

        if size > Config.MAX_CONTENT_LENGTH:

            flash(
                "The file exceeds the 100 MB limit.",
                "error"
            )

            return redirect(
                url_for("upload.upload_page")
            )

        integrity_key = load_integrity_key()

        stored_name = uuid.uuid4().hex + ".vault"

        storage = Path(Config.STORAGE_FOLDER)

        storage.mkdir(
            parents=True,
            exist_ok=True
        )

        final_path = storage / stored_name

        fd, temp_name = tempfile.mkstemp(
            dir=storage,
            suffix=".tmp"
        )

        os.close(fd)

        temporary_path = Path(temp_name)

        with open(
            temporary_path,
            "wb"
        ) as encrypted_output:

            encrypt_file_chunks(
                uploaded.stream,
                encrypted_output,
                chunk_size=Config.CHUNK_SIZE
            )

            encrypted_output.flush()

            os.fsync(
                encrypted_output.fileno()
            )

        signature = calculate_file_hmac(
            temporary_path,
            integrity_key
        )

        os.replace(
            temporary_path,
            final_path
        )

        temporary_path = None

        try:

            create_file_record(
                int(current_user.id),
                filename,
                stored_name,
                size,
                signature
            )

        except Exception:

            final_path.unlink(
                missing_ok=True
            )

            raise

        flash(
            "File encrypted and stored successfully.",
            "success"
        )

        return redirect(
            url_for("files_page")
        )

    except Exception:

        if temporary_path and temporary_path.exists():

            temporary_path.unlink(
                missing_ok=True
            )

        current_app.logger.exception(
            "Upload failed for user ID %s",
            current_user.id
        )

        flash(
            "Upload could not be completed. Check the configuration and try again.",
            "error"
        )

        return redirect(
            url_for("upload.upload_page")
        )
