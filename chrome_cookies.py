"""Read decrypted Chrome cookies on macOS."""

import argparse
import hashlib
import os
import sqlite3
import shutil
import subprocess
import tempfile

_COOKIE_DB = "~/Library/Application Support/Google/Chrome/Default/Cookies"


def _get_aes_key() -> bytes | None:
    """Get Chrome AES key from macOS Keychain via PBKDF2."""
    result = subprocess.run(
        ["security", "find-generic-password", "-w", "-s", "Chrome Safe Storage", "-a", "Chrome"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    chrome_pass = result.stdout.strip()
    return hashlib.pbkdf2_hmac("sha1", chrome_pass.encode(), b"saltysalt", 1003, dklen=16)


def _decrypt_value(enc_value: bytes, aes_key: bytes) -> str | None:
    """Decrypt a v10-prefixed Chrome cookie value."""
    if not enc_value or enc_value[:3] != b"v10":
        return None
    payload = enc_value[3:]
    result = subprocess.run(
        ["openssl", "enc", "-aes-128-cbc", "-d", "-K", aes_key.hex(), "-iv", "00" * 16, "-nopad"],
        input=payload, capture_output=True,
    )
    if result.returncode != 0:
        return None
    text = result.stdout.decode("utf-8", errors="ignore")
    while text and ord(text[-1]) < 32:
        text = text[:-1]
    return text or None


def _open_cookie_db() -> tuple[sqlite3.Connection, str] | None:
    """Copy Chrome cookie DB to tmp and open it. Caller must call _cleanup_cookie_db()."""
    cookie_db = os.path.expanduser(_COOKIE_DB)
    if not os.path.exists(cookie_db):
        return None
    fd, tmp_path = tempfile.mkstemp(suffix=".db", prefix="chrome_cookie_")
    os.close(fd)
    shutil.copy2(cookie_db, tmp_path)
    return sqlite3.connect(tmp_path), tmp_path


def _cleanup_cookie_db(tmp_path: str) -> None:
    """Remove the temporary cookie DB copy."""
    if os.path.exists(tmp_path):
        os.remove(tmp_path)


def get_cookie(host: str, name: str) -> str | None:
    """Read a decrypted Chrome cookie value by host and name (macOS only).

    host is matched with LIKE '%host%' so partial domain works
    (e.g. 'github.com' matches both '.github.com' and 'github.com').
    """
    aes_key = _get_aes_key()
    if aes_key is None:
        return None

    result = _open_cookie_db()
    if result is None:
        return None
    conn, tmp_path = result
    try:
        cursor = conn.execute(
            "SELECT encrypted_value FROM cookies WHERE host_key LIKE ? AND name=? LIMIT 1",
            (f"%{host}%", name),
        )
        row = cursor.fetchone()
    finally:
        conn.close()
        _cleanup_cookie_db(tmp_path)

    if not row or not row[0]:
        return None
    return _decrypt_value(row[0], aes_key)


def list_cookies(host: str) -> list[tuple[str, str, str | None]]:
    """List all cookies for a host with decrypted values (macOS only).

    Returns list of (host_key, name, decrypted_value) tuples.
    host is matched with LIKE '%host%'.
    """
    aes_key = _get_aes_key()
    if aes_key is None:
        return []

    result = _open_cookie_db()
    if result is None:
        return []
    conn, tmp_path = result
    try:
        cursor = conn.execute(
            "SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE ?",
            (f"%{host}%",),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()
        _cleanup_cookie_db(tmp_path)

    results = []
    for host_key, name, enc_value in rows:
        decrypted = _decrypt_value(enc_value, aes_key)
        results.append((host_key, name, decrypted))
    return results


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Read Chrome cookies on macOS")
    sub = parser.add_subparsers(dest="command", required=True)

    get_parser = sub.add_parser("get", help="Get a specific cookie value")
    get_parser.add_argument("host", help="Domain to match (partial, e.g. 'github.com')")
    get_parser.add_argument("name", help="Cookie name")

    list_parser = sub.add_parser("list", help="List all cookies for a host")
    list_parser.add_argument("host", help="Domain to match (partial, e.g. 'github.com')")

    args = parser.parse_args()

    if args.command == "get":
        value = get_cookie(args.host, args.name)
        if value is None:
            print("Cookie not found.")
        else:
            print(value)
    elif args.command == "list":
        cookies = list_cookies(args.host)
        if not cookies:
            print("No cookies found.")
        else:
            for host_key, name, value in cookies:
                display = value if value else "(decrypt failed)"
                print(f"{host_key}\t{name}\t{display}")


if __name__ == "__main__":
    main()
