# Chrome Cookie Reader

[English](README.md)

macOS Chrome 쿠키를 복호화하여 읽는 Python 모듈.

## Requirements

- Python 3.10+
- macOS (Keychain 사용)
- [cryptography](https://pypi.org/project/cryptography/) (pip 설치 시 자동 포함)

## Installation

```bash
# 권장: 격리된 venv에 CLI를 PATH에 설치
pipx install ~/home/chrome-cookie-reader      # 로컬
pipx install git+https://github.com/WoojinAhn/chrome-cookie-reader.git  # GitHub에서

# 또는 Python 패키지로 설치 (모듈 import용)
pip install -e ~/home/chrome-cookie-reader
```

## Usage

### CLI

```bash
# 도메인의 모든 쿠키 목록 조회
chrome-cookies list github.com

# 특정 쿠키 값 조회
chrome-cookies get github.com session_id
```

### Module

```python
from chrome_cookies import get_cookie, list_cookies

# 단일 쿠키 조회 (str | None 반환)
value = get_cookie("github.com", "session_id")

# 도메인의 모든 쿠키 조회 ((host_key, name, value) 튜플 리스트 반환)
cookies = list_cookies("github.com")
```

호스트는 부분 매칭 — `github.com`을 넣으면 `.github.com`과 `github.com` 모두 매칭됨.

## How It Works

1. macOS Keychain에서 Chrome Safe Storage 비밀번호 조회
2. PBKDF2-SHA1로 AES-128-CBC 키 유도
3. Chrome Cookies SQLite DB를 임시 파일로 복사 (동시 접근 안전)
4. AES-128-CBC로 쿠키 값 복호화

## License

MIT
