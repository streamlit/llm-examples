import os
import json
import pytest

import auth_encrypt


def cleanup_user(username: str):
    users = auth_encrypt._load_users()
    if username in users:
        users.pop(username, None)
        auth_encrypt._save_users(users)
    enc_path = auth_encrypt._USER_DATA_DIR / f"{username}.enc"
    if enc_path.exists():
        enc_path.unlink()


def test_create_verify_decrypt_cycle():
    username = "pytest_user"
    password = "test-pass-123"
    plaintext = b"Secret data for pytest"

    # ensure clean slate
    cleanup_user(username)

    ok, msg = auth_encrypt.create_user(username, password, plaintext)
    assert ok, f"create_user failed: {msg}"

    # correct verify
    ok, key = auth_encrypt.verify_user(username, password)
    assert ok and key is not None

    # wrong password should fail
    ok_bad, _ = auth_encrypt.verify_user(username, "wrong-password")
    assert not ok_bad

    # decrypt
    ok2, pt, m = auth_encrypt.decrypt_user_file(username, key)
    assert ok2, f"decrypt failed: {m}"
    assert pt == plaintext

    # cleanup
    cleanup_user(username)
