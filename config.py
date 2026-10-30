
import os
from pathlib import Path
from dotenv import load_dotenv


# Find the main VAULTEX project folder
BASE_DIR = Path(__file__).resolve().parent

# Load private environment variables from .env
load_dotenv(BASE_DIR / ".env")


class Config:

    # Flask security
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # Encryption keys
    ENCRYPTION_KEY_ENV = "VAULTEX_ENCRYPTION_KEY"
    INTEGRITY_KEY_ENV = "VAULTEX_INTEGRITY_KEY"

    # Storage and database locations
    STORAGE_FOLDER = BASE_DIR / "storage" / "encrypted_files"
    DATABASE_PATH = BASE_DIR / "database" / "vaultex.db"

    # File upload settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    CHUNK_SIZE = 1024 * 1024
    MAX_CHUNK_SIZE = 4 * 1024 * 1024

    # Supported file extensions
    ALLOWED_EXTENSIONS = {
        "pdf",
        "docx",
        "txt",
        "jpg",
        "jpeg",
        "png",
        "zip",
        "csv",
        "xlsx"
    }

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = (
        os.getenv("VAULTEX_HTTPS", "false").lower() == "true"
    )

    PERMANENT_SESSION_LIFETIME = 1800

    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600


# Create encrypted storage folder if it doesn't exist
Config.STORAGE_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)
