"""Read decrypted Chrome cookies on macOS."""

import hashlib
import os
import sqlite3
import subprocess


def get_cookie(host: str, name: str) -> str | None:
    """Read a decrypted Chrome cookie value by host and name (macOS only).

    Uses Keychain to get Chrome's encryption password, derives an AES key,
    copies the cookie DB to avoid lock issues, and decrypts via openssl.
    """
    cookie_db = os.path.expanduser(
        "~/Library/Application Support/Google/Chrome/Default/Cookies"
    )
    if not os.path.exists(cookie_db):
        return None

    # Get Chrome Safe Storage password from macOS Keychain
    result = subprocess.run(
        ["security", "find-generic-password", "-w", "-s", "Chrome Safe Storage", "-a", "Chrome"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    chrome_pass = result.stdout.strip()

    # Derive AES key (PBKDF2-SHA1, 1003 iterations, 16-byte key)
    aes_key = hashlib.pbkdf2_hmac("sha1", chrome_pass.encode(), b"saltysalt", 1003, dklen=16)

    # Read encrypted cookie (copy DB to avoid Chrome lock)
    tmp_db = "/tmp/_chrome_cookie_reader.db"
    subprocess.run(["cp", cookie_db, tmp_db], capture_output=True)
    try:
        conn = sqlite3.connect(tmp_db)
        cursor = conn.execute(
            "SELECT encrypted_value FROM cookies WHERE host_key=? AND name=?",
            (host, name),
        )
        row = cursor.fetchone()
        conn.close()
    finally:
        os.remove(tmp_db)

    if not row or not row[0]:
        return None

    enc_value = row[0]
    if enc_value[:3] != b"v10":
        return None

    # Decrypt with AES-128-CBC (IV = 16 zero bytes, no padding)
    payload = enc_value[3:]
    result = subprocess.run(
        ["openssl", "enc", "-aes-128-cbc", "-d", "-K", aes_key.hex(), "-iv", "00" * 16, "-nopad"],
        input=payload, capture_output=True,
    )
    if result.returncode != 0:
        return None

    # Strip PKCS#7 padding / trailing control characters
    text = result.stdout.decode("utf-8", errors="ignore")
    while text and ord(text[-1]) < 32:
        text = text[:-1]

    return text or None
