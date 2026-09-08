# Pydantic

Pydantic: 파이썬 생태계의 핵심 데이터 유효성 검사 도구. 데이터 검증. API 요청/응답 검증에도 사용. 외부의 신뢰할 수 없는 데이터(API 요청, DB 결과, AI 생성 텍스트 등)를 신뢰할 수 있는 파이썬 객체로 맵핑.

Source: https://wikidocs.net/226652


<img src="https://static.wikidocs.net/images/page/226652/image_202604272122.png">


Pydantic은 파이썬의 타입 힌트(Type Hints)를 활용하여 데이터 유효성 검사(Validation)와 설정 관리를 수행하는 가장 핵심적인 라이브러리입니다.

2026년 기준, Pydantic은 파이썬 생태계 전체의 성능을 견인하는 가장 중요한 심장이 되었습니다. FastAPI의 기반 기술일 뿐만 아니라 LangChain, OpenAI 파이썬 클라이언트 등 데이터의 정확성과 변환이 필요한 거의 모든 주요 라이브러리가 내부적으로 Pydantic을 사용하고 있습니다.

Pydantic v2 및 최신 (2026년) 주요 변화 과거 순수 파이썬으로 작성되었던 v1을 버리고, 핵심 검증 엔진(pydantic-core)을 Rust 언어로 완전히 재작성한 v2가 완벽한 표준으로 자리 잡았습니다.

1. 압도적인 속도: Rust 코어 덕분에 기존 대비 데이터 검증 속도가 최소 5배에서 최대 50배까지 빨라졌습니다.
2. 스트리밍(Streaming) 유효성 검사: LLM(대규모 언어 모델)이 생성하는 불완전한 JSON 데이터 조각들을 실시간으로 파싱하고 검증할 수 있는 기능(jiter 결합)이 추가되어, AI 서비스의 응답 지연 시간(Latency)을 획기적으로 줄였습니다.
3. 엄격한 모드(Strict Mode): 자동 형변환(예: 문자열 "123"을 정수 123으로 자동 변환)을 방지하고 정확한 데이터 타입만 허용하는 strict=True 기능이 대폭 강화되었습니다.
4. 메서드 이름 변경: v1에서 사용되던 .dict()나 .json() 같은 혼동을 주던 메서드들이 `.model_dump()` 및 `.model_dump_json()`으로 직관적으로 변경되었습니다.

주요 기능

- 타입 힌트 기반 검증: 개발자가 파이썬 표준 문법(타입 힌트)만 작성하면 Pydantic이 런타임에 자동으로 타입을 강제하고 오류를 잡아줍니다.
- 복잡한 직렬화/역직렬화: JSON, 딕셔너리 등의 데이터를 파이썬 객체로 쉽게 변환하며, 반환할 데이터를 세밀하게 필터링(특정 필드 제외, 별칭 사용 등)할 수 있습니다.
- 환경 변수 관리 (pydantic-settings): `.env` 파일이나 시스템 환경 변수를 타입 안전성이 보장된 파이썬 객체로 불러오는 가장 완벽한 방법을 제공합니다.

설치 방법

```bash
uv add pydantic pydantic-settings
```

예제 코드 (최신 Pydantic v2 문법)

```python
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError

class User(BaseModel):
    id: int
    name: str = Field(..., min_length=2, max_length=50)
    # email 필드는 이메일 형식 검증을 지원합니다 (email-validator 필요)
    email: str 
    signup_ts: datetime | None = None

    # Strict 모드 옵션 설정
    model_config = {
        "strict": False  # True로 설정 시 자동 형변환 불가
    }

# 1. 정상적인 데이터 파싱 (문자열 '123'이 자동으로 정수 123으로 형변환됨)
user = User(id='123', name='John Doe', email='john@example.com')
print(user.id)  # 출력: 123 (정수형)

# 2. 데이터를 딕셔너리나 JSON으로 직렬화 (v2 최신 문법)
print(user.model_dump()) 
print(user.model_dump_json(exclude_none=True)) # None인 필드는 제외하고 JSON 변환

# 3. 잘못된 데이터 검증
try:
    bad_user = User(id=456, name='J', email='not_an_email')
except ValidationError as e:
    print(e.json()) # name의 최소 길이(2) 위반 에러 출력
```

결론: Pydantic은 단순히 데이터가 올바른지 확인하는 도구를 넘어, 외부의 신뢰할 수 없는 데이터(API 요청, DB 결과, AI 생성 텍스트 등)를 신뢰할 수 있는 파이썬 객체로 맵핑하는 가장 빠르고 우아한 방어막입니다. Rust 코어 도입 이후 성능이라는 유일한 약점마저 극복하면서, 모던 파이썬 개발에서 절대 빠질 수 없는 필수 라이브러리가 되었습니다.

