# Chrome Cookie Reader

> **Archived.** 동일한 기능을 더 잘 제공하는 [pycookiecheat](https://github.com/n8henrie/pycookiecheat)를 사용하세요. 이 프로젝트는 학습 겸 개인 유틸리티로 시작했지만, 이미 잘 돌아가는 바퀴를 다시 만들 이유는 없습니다. 만약 pycookiecheat가 더 이상 관리되지 않는 날이 온다면, 그때 다시 꺼내볼 수도 있습니다.

[English](README.md)

macOS Chrome 쿠키를 복호화하여 읽는 Python 모듈.

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

1. macOS Keychain에서 Chrome Safe Storage 비밀번호 조회
2. PBKDF2-SHA1로 AES-128-CBC 키 유도
3. Chrome Cookies SQLite DB를 임시 파일로 복사 (동시 접근 안전)
4. AES-128-CBC로 쿠키 값 복호화

## License

MIT
