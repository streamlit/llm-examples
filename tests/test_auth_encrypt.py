import pytest
from cryptography.exceptions import InvalidTag

import auth_encrypt


def test_create_decrypt_key():
    """Test salt generation and key derivation."""
    password = "test-pass-123"
    
    # Generate new salt and key
    salt1, key1 = auth_encrypt.create_decrypt_key(password)
    assert len(salt1) == 16
    assert len(key1) == 32
    
    # Same password with different salt produces different key
    salt2, key2 = auth_encrypt.create_decrypt_key(password)
    assert salt1 != salt2
    assert key1 != key2
    
    # Same password with same salt produces same key
    _, key3 = auth_encrypt.create_decrypt_key(password, salt=salt1)
    assert key1 == key3


def test_encrypt_decrypt_cycle():
    """Test full encrypt/decrypt cycle with correct password."""
    password = "s3cret-password"
    plaintext = b"Secret data for pytest"
    
    # Generate salt and encrypt
    salt, _ = auth_encrypt.create_decrypt_key(password)
    encrypted = auth_encrypt.encrypt_history(plaintext, password, salt)
    
    # Verify encrypted data is longer (nonce + ciphertext + auth tag)
    assert len(encrypted) > len(plaintext)
    assert encrypted != plaintext
    
    # Decrypt with correct password
    decrypted = auth_encrypt.decrypt_history(encrypted, password, salt)
    assert decrypted == plaintext


def test_wrong_password_fails():
    """Test that wrong password raises exception during decryption."""
    password = "correct-password"
    wrong_password = "wrong-password"
    plaintext = b"Secret message"
    
    salt, _ = auth_encrypt.create_decrypt_key(password)
    encrypted = auth_encrypt.encrypt_history(plaintext, password, salt)
    
    # Wrong password should raise InvalidTag
    with pytest.raises(InvalidTag):
        auth_encrypt.decrypt_history(encrypted, wrong_password, salt)


def test_wrong_salt_fails():
    """Test that wrong salt raises exception during decryption."""
    password = "password123"
    plaintext = b"Another secret"
    
    salt, _ = auth_encrypt.create_decrypt_key(password)
    encrypted = auth_encrypt.encrypt_history(plaintext, password, salt)
    
    # Different salt should fail
    wrong_salt, _ = auth_encrypt.create_decrypt_key(password)
    with pytest.raises(InvalidTag):
        auth_encrypt.decrypt_history(encrypted, password, wrong_salt)
