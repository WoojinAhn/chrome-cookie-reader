# Chrome Cookie Reader

[한국어](README_ko.md)

A Python module to decrypt and read Chrome cookies on macOS.

## Requirements

- Python 3.10+
- macOS (uses Keychain + openssl)
- No external dependencies (stdlib only)

## Usage

### CLI

```bash
# List all cookies for a domain
python3 chrome_cookies.py list github.com

# Get a specific cookie value
python3 chrome_cookies.py get github.com session_id
```

### Module

```python
from chrome_cookies import get_cookie, list_cookies

# Get a single cookie (returns str | None)
value = get_cookie("github.com", "session_id")

# List all cookies for a domain (returns list of (host_key, name, value) tuples)
cookies = list_cookies("github.com")
```

Host matching is partial — `github.com` matches both `.github.com` and `github.com`.

## How It Works

1. Retrieve Chrome Safe Storage password from macOS Keychain
2. Derive AES-128-CBC key via PBKDF2-SHA1
3. Copy Chrome Cookies SQLite DB to avoid lock contention
4. Decrypt cookie values with openssl
