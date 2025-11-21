"""
Simple auth + file encryption helper.

Features:
- Create user: generates salt, derives a key from password (PBKDF2-HMAC-SHA256), stores verifier and encrypts provided bytes with AES-GCM.
- Verify user: derives key and compares against stored verifier.
- Decrypt user file: locate encrypted file and decrypt with derived key.

Storage:
- users.json in repository root stores entries like {
    username: { salt: base64, kdf_iterations: int, pw_verifier: base64, enc_filename: str }
}

This file is intentionally small and dependency-only; do not use in production without proper audits.
"""
from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Config
_ROOT = Path(__file__).resolve().parent
_USERS_FILE = _ROOT / "users.json"
_USER_DATA_DIR = _ROOT / "user_data"
_USER_DATA_DIR.mkdir(exist_ok=True)


def _load_users() -> dict:
    if not _USERS_FILE.exists():
        return {}
    with _USERS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_users(data: dict) -> None:
    with _USERS_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _derive_key(password: str, salt: bytes, iterations: int = 200_000) -> bytes:
    """Derive a 32-byte key from password and salt using PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode("utf-8"))


def _verify_key(password: str, salt: bytes, expected: bytes, iterations: int = 200_000) -> bool:
    """Return True if password derives to expected key. Uses exception semantics from KDF verify via try/except."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    try:
        kdf.verify(password.encode("utf-8"), expected)
        return True
    except Exception:
        return False


def create_user(username: str, password: str, plaintext: bytes) -> Tuple[bool, str]:
    """Create a new user entry and encrypt provided plaintext.

    Returns (success, message).
    If username exists, returns False.
    """
    users = _load_users()
    if username in users:
        return False, "username already exists"

    salt = os.urandom(16)
    iterations = 200_000
    key = _derive_key(password, salt, iterations=iterations)

    # encrypt
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plaintext, associated_data=None)

    enc_filename = f"{username}.enc"
    enc_path = _USER_DATA_DIR / enc_filename
    # store as base64: nonce + ciphertext
    with enc_path.open("wb") as f:
        f.write(base64.b64encode(nonce + ct))

    users[username] = {
        "salt": base64.b64encode(salt).decode("utf-8"),
        "kdf_iterations": iterations,
        "pw_verifier": base64.b64encode(key).decode("utf-8"),
        "enc_filename": enc_filename,
    }
    _save_users(users)
    return True, f"user created, encrypted file saved to user_data/{enc_filename}"


def verify_user(username: str, password: str) -> Tuple[bool, Optional[bytes]]:
    """Verify username/password. If ok, returns (True, key) where key is the derived key used for encryption/decryption.
    If failure, (False, None).
    """
    users = _load_users()
    info = users.get(username)
    if not info:
        return False, None
    salt = base64.b64decode(info["salt"])
    iterations = int(info.get("kdf_iterations", 200_000))
    expected = base64.b64decode(info["pw_verifier"])
    # verify
    ok = _verify_key(password, salt, expected, iterations=iterations)
    if not ok:
        return False, None
    key = _derive_key(password, salt, iterations=iterations)
    return True, key


def decrypt_user_file(username: str, key: bytes) -> Tuple[bool, Optional[bytes], str]:
    """Attempt to locate and decrypt the user's encrypted file.

    Returns (success, plaintext_bytes_or_None, message).
    """
    users = _load_users()
    info = users.get(username)
    if not info:
        return False, None, "user not found"
    enc_filename = info.get("enc_filename")
    if not enc_filename:
        return False, None, "no encrypted file for user"
    enc_path = _USER_DATA_DIR / enc_filename
    if not enc_path.exists():
        return False, None, f"encrypted file {enc_filename} missing"
    data = base64.b64decode(enc_path.read_bytes())
    nonce = data[:12]
    ct = data[12:]
    aes = AESGCM(key)
    try:
        pt = aes.decrypt(nonce, ct, associated_data=None)
        return True, pt, "decrypted"
    except Exception as e:
        return False, None, f"decryption failed: {e}"


if __name__ == "__main__":
    # Quick local demo
    demo_user = "alice"
    demo_pw = "s3cret!"
    demo_text = b"Hello Alice! This is a secret document."

    ok, msg = create_user(demo_user, demo_pw, demo_text)
    print(ok, msg)
    ok, key = verify_user(demo_user, demo_pw)
    print("verify", ok)
    if ok:
        ok2, pt, m = decrypt_user_file(demo_user, key)
        print(ok2, m)
        if ok2:
            print(pt.decode())
