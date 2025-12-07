"""
Simple history encryption helper using password-based key derivation.

Public API:
- create_decrypt_key(password, salt=None): Generate salt and derive encryption key from password
- encrypt_history(plaintext, password, salt): Encrypt bytes using AES-GCM with PBKDF2-derived key
- decrypt_history(ciphertext, password, salt): Decrypt bytes using AES-GCM with PBKDF2-derived key

"""
from __future__ import annotations

import base64
import os
from typing import Tuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def create_decrypt_key(password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
    """Generate a random salt and derive a 32-byte encryption key from password using PBKDF2-HMAC-SHA256.
    
    Args:
        password: User password
        salt: Optional salt bytes (16 bytes). If None, generates random salt.
    
    Returns:
        (salt, key) tuple where:
        - salt: 16-byte random salt (store this with encrypted data)
        - key: 32-byte derived key for encryption/decryption
    """
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    key = kdf.derive(password.encode("utf-8"))
    return salt, key


def encrypt_history(plaintext: bytes, password: str, salt: bytes) -> bytes:
    """Encrypt plaintext using AES-GCM with a key derived from password and salt.
    
    Args:
        plaintext: Data to encrypt
        password: User password
        salt: 16-byte salt (from create_decrypt_key)
    
    Returns:
        Encrypted bytes in format: nonce (12 bytes) + ciphertext
    """
    _, key = create_decrypt_key(password, salt)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(nonce, plaintext, associated_data=None)
    return nonce + ciphertext


def decrypt_history(encrypted_data: bytes, password: str, salt: bytes) -> bytes:
    """Decrypt data encrypted with encrypt_history.
    
    Args:
        encrypted_data: Encrypted bytes (nonce + ciphertext)
        password: User password
        salt: 16-byte salt used during encryption
    
    Returns:
        Decrypted plaintext bytes
        
    Raises:
        cryptography.exceptions.InvalidTag: If password/salt incorrect or data corrupted
    """
    _, key = create_decrypt_key(password, salt)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    aes = AESGCM(key)
    plaintext = aes.decrypt(nonce, ciphertext, associated_data=None)
    return plaintext


if __name__ == "__main__":
    # Quick local demo
    demo_pw = "s3cret!"
    demo_text = b"Hello! This is a secret document."

    # Create key with random salt
    salt, key = create_decrypt_key(demo_pw)
    print(f"Generated salt: {base64.b64encode(salt).decode()}")
    
    # Encrypt
    encrypted = encrypt_history(demo_text, demo_pw, salt)
    print(f"Encrypted {len(encrypted)} bytes")
    
    # Decrypt
    decrypted = decrypt_history(encrypted, demo_pw, salt)
    print(f"Decrypted: {decrypted.decode()}")
    
    # Verify wrong password fails
    try:
        decrypt_history(encrypted, "wrong-password", salt)
        print("ERROR: Should have failed!")
    except Exception as e:
        print(f"Wrong password correctly rejected: {type(e).__name__}")
