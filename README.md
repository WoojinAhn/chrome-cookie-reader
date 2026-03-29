# Chrome Cookie Reader

> **Archived.** Use [pycookiecheat](https://github.com/n8henrie/pycookiecheat) instead — a mature, well-maintained library that does the same thing and more. This project was a learning exercise and personal utility; there's no reason to reinvent what already works well. If pycookiecheat ever becomes unmaintained, I may revisit this.

[한국어](README_ko.md)

A Python module to decrypt and read Chrome cookies on macOS.

## Installation

```bash
pipx install git+https://github.com/WoojinAhn/chrome-cookie-reader.git
```

## Usage

### CLI

```bash
chrome-cookies list github.com
chrome-cookies get github.com session_id
```

### Module

```python
from chrome_cookies import get_cookie, list_cookies

value = get_cookie("github.com", "session_id")
cookies = list_cookies("github.com")
```

## How It Works

1. Retrieve Chrome Safe Storage password from macOS Keychain
2. Derive AES-128-CBC key via PBKDF2-SHA1
3. Copy Chrome Cookies SQLite DB to a temp file (concurrent-safe)
4. Decrypt cookie values with AES-128-CBC

## License

MIT
