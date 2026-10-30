
# VAULTEX
### Encrypted File Transfer & Secure File Storage

**Your files. Your privacy. Your control.**

VAULTEX is a Python-based web application designed to provide secure file storage and encrypted file transfer.

The application uses AES-256-GCM encryption, HMAC-SHA256 integrity verification, password hashing and user authentication to protect stored files.

---

## 1. Project Overview

VAULTEX allows users to:

- Create an account and securely sign in.
- Upload supported files.
- Encrypt files before storing them on the server.
- Store encrypted files separately from the database.
- Verify file integrity before decryption.
- Download and retrieve original files.
- Access a private file library.

---

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| HTML | Page structure |
| CSS | User interface and styling |
| JavaScript | Frontend interactions |
| SQLite | Database |
| Cryptography | AES-256-GCM encryption |
| HMAC-SHA256 | Integrity verification |
| Flask-Login | User authentication |
| Flask-WTF | CSRF protection |
| TLS/HTTPS | Secure communication when configured |

---

## 3. Security Features

### AES-256-GCM Encryption

VAULTEX uses AES-256-GCM authenticated encryption to protect file contents.

Large files are processed in chunks. Each encrypted chunk uses a unique random nonce and authenticated metadata.

### HMAC-SHA256 Integrity Verification

A separate secret key generates an HMAC signature for each encrypted file.

The signature is verified before the file is decrypted.

### Password Security

Passwords are stored as password hashes using Werkzeug rather than plain text.

### User Authentication

Flask-Login manages authenticated user sessions.

### File Access Control

Users can retrieve only files associated with their own account.

### CSRF Protection

Flask-WTF protects state-changing form submissions against Cross-Site Request Forgery.

### HTTPS/TLS

HTTPS must be configured through a trusted TLS endpoint before deployment. Local development does not automatically enable HTTPS.

---

## 4. Project Structure

```text
VAULTEX/
│
├── app.py
├── config.py
├── extensions.py
├── models.py
├── requirements.txt
├── generate_secrets.py
├── README.md
├── .env
├── .env.example
├── .gitignore
│
├── database/
│   ├── __init__.py
│   └── database.py
│
├── encryption/
│   ├── __init__.py
│   ├── key_manager.py
│   ├── aes_encryption.py
│   └── integrity.py
│
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── upload.py
│   └── download.py
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── files.html
│   ├── security.html
│   └── settings.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│
├── storage/
│   └── encrypted_files/
│
├── logs/
│
└── tests/
    ├── test_encryption.py
    ├── test_integrity.py
    └── test_upload.py
```

---

## 5. Configuration and Secret Management

VAULTEX uses environment variables for its application and cryptographic secrets.

The private `.env` file must contain:

- `FLASK_SECRET_KEY`
- `VAULTEX_ENCRYPTION_KEY`
- `VAULTEX_INTEGRITY_KEY`

The encryption and integrity keys must be different.

Never upload `.env` to GitHub or share your secret keys.

The `.env.example` file is only a configuration template.

---

## 6. File Processing Workflow

1. User selects a file.
2. The application validates the filename extension and file size.
3. The file is encrypted using AES-256-GCM.
4. Encrypted chunks are written to server storage.
5. HMAC-SHA256 is calculated for the encrypted file.
6. File information and its integrity signature are stored in SQLite.
7. During download, ownership is checked.
8. The encrypted file's HMAC is verified.
9. The file is decrypted and returned to the authenticated user.

---

## 7. Installation and Execution

The following setup instructions are for local development.

1. Install Python 3.12 or a compatible version.
2. Install the packages listed in `requirements.txt`.
3. Generate fresh application and cryptographic secrets using `generate_secrets.py`.
4. Store the generated values in a private `.env` file.
5. Start the Flask application using the configured development environment.

Detailed setup and testing will be completed after the project files are assembled.

---

## 8. Testing

The `tests/` directory contains automated tests for:

- Encryption and decryption.
- Incorrect encryption keys.
- Chunk-based file processing.
- Corrupted encrypted data.
- HMAC integrity verification.
- File-extension validation.

---

## 9. Limitations and Future Improvements

Potential improvements include:

- File-content and MIME-type validation.
- Login rate limiting.
- Secure key rotation and backup.
- Resumable uploads.
- Improved temporary-file cleanup.
- Production HTTPS deployment.
- Security auditing and penetration testing.
- Multi-factor authentication.

---

## 10. Project Objective

The primary objective of VAULTEX is to demonstrate how encryption, integrity verification, authentication and access control can be combined to build a secure file storage and transfer application.

**VAULTEX — Your files. Your privacy. Your control.**
```
