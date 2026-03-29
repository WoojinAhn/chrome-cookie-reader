# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

macOS Chrome 쿠키를 복호화하여 읽는 단일 파일 Python 모듈 (`chrome_cookies.py`). `cryptography` 라이브러리로 AES 복호화 수행.

## Requirements

- Python 3.10+ (union type `str | None` 사용)
- macOS only (Keychain `security` CLI 의존)
- `cryptography` 라이브러리 (`pipx install .` 또는 `pip install -e .`로 설치)

## Run

```bash
# CLI (requires pipx install or pip install -e .)
chrome-cookies list github.com
chrome-cookies get github.com session_id

# Module (requires pip install -e .)
python3 -c "from chrome_cookies import get_cookie, list_cookies; print(list_cookies('github.com'))"
```

No build step, no tests, no linting configured.

## Architecture

단일 파일 `chrome_cookies.py`에 공개 함수 2개 + 내부 헬퍼 4개:

**공개 API:**
- `get_cookie(host, name)` → `str | None` — 단일 쿠키 조회
- `list_cookies(host)` → `list[tuple[str, str, str | None]]` — 도메인의 모든 쿠키 조회 (host_key, name, value)

**내부 헬퍼:**
- `_get_aes_key()` — Keychain → PBKDF2 키 유도
- `_decrypt_value()` — v10 prefix 쿠키 AES-128-CBC 복호화 (`cryptography` 라이브러리 사용)
- `_open_cookie_db()` / `_cleanup_cookie_db()` — DB 복사/정리

**host 매칭:** `LIKE '%host%'` 부분 매칭. `.github.com`과 `github.com`을 구분할 필요 없음.

**암호화 파이프라인:** Keychain 비밀번호 → PBKDF2-SHA1 (salt: `saltysalt`, 1003 iterations) → AES-128-CBC (IV: 16 zero bytes) → PKCS#7 unpadding (`cryptography` 라이브러리). 쿠키 값은 `v10` prefix로 시작.

## Docs

- `README.md` — English
- `README_ko.md` — 한국어
