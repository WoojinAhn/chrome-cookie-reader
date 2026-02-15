# Chrome Cookie Reader

macOS Chrome 쿠키를 복호화하여 읽는 Python 모듈.

## Requirements

- Python 3.10+
- macOS (Keychain + openssl 사용)
- No external dependencies (stdlib only)

## Usage

```python
from chrome_cookies import get_cookie

value = get_cookie("example.com", "session_id")
```

## How It Works

1. macOS Keychain에서 Chrome Safe Storage 비밀번호 조회
2. PBKDF2-SHA1로 AES-128-CBC 키 유도
3. Chrome Cookies SQLite DB 복사 (lock 회피)
4. openssl로 쿠키 값 복호화
