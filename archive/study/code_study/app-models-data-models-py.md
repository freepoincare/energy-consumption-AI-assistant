# app/models/data_models.py

`app/models/data_models.py`는 **API에서 주고받는 데이터의 형식(스키마)** 을 정의하는 파일입니다.

쉽게 말하면 이 파일은:

- 어떤 입력을 받을지
- 어떤 형식으로 검증할지
- 어떤 형태로 응답을 줄지

를 정해주는 **데이터 계약서** 역할을 합니다.

---

# 파일 전체 목적

이 파일은 Pydantic을 사용해서 에너지 데이터 관련 모델을 정의합니다.

주요 모델은:

- `EnergyDataCreate` → 새 데이터 생성 요청
- `EnergyDataUpdate` → 기존 데이터 수정 요청
- `EnergyDataResponse` → 단일 데이터 응답
- `EnergyDataListResponse` → 여러 데이터 목록 응답
- `SummaryResponse` → 통계 요약 응답

---

# 1. 파일 맨 위 주석

```python
"""
Pydantic schemas for daily energy data operations and summaries.
Data unit: (date, value, memo) where value = daily electricity consumption in kWh.
"""
```

## 설명
이건 **문서용 문자열(docstring)** 입니다.

- 이 파일이 무엇을 위한 파일인지 설명합니다.
- “일별 에너지 데이터 작업과 요약을 위한 Pydantic 스키마”
- 데이터 단위는 `(date, value, memo)`이고
- `value`는 **하루 전기 사용량(kWh)** 이라고 알려줍니다.

즉, 이 파일을 처음 보는 개발자에게  
“아, 이 파일은 에너지 데이터의 입력/출력 형식을 정의하는 곳이구나”  
하고 알려주는 안내문입니다.

---

# 2. import 부분

```python
from pydantic import BaseModel, Field, field_validator
```

## 설명
Pydantic에서 필요한 도구를 가져옵니다.

### `BaseModel`
- 모든 Pydantic 모델의 부모 클래스입니다.
- 우리가 만드는 클래스가 이걸 상속받으면:
  - 자동 검증
  - 타입 변환
  - JSON 변환
  - 문서화
  같은 기능을 쓸 수 있습니다.

### `Field`
- 각 필드에 추가 정보와 제약 조건을 붙일 때 사용합니다.
- 예:
  - 최소값
  - 설명(description)
  - 예시(example)
  - 최대 길이(max_length)

### `field_validator`
- 특정 필드를 직접 검증하는 데코레이터입니다.
- 여기서는 `date` 형식을 검사하는 데 사용됩니다.

---

```python
from typing import Optional, List, Dict, Any
```

## 설명
타입 힌트를 위해 가져옵니다.

### `Optional`
- 값이 있을 수도 있고 없을 수도 있다는 뜻
- 예:
  - `Optional[str]`
  - 문자열 또는 `None`

### `List`
- 리스트 타입
- 예:
  - `List[EnergyDataResponse]`

### `Dict`
- 딕셔너리 타입
- 예:
  - `Dict[str, Any]`

### `Any`
- 어떤 타입이든 가능하다는 뜻
- 구조가 유동적인 데이터에 자주 사용합니다

---

```python
from datetime import datetime
```

## 설명
날짜 문자열이 실제로 유효한 날짜인지 검사할 때 사용합니다.

예:
- `"2026-09-01"` → 유효
- `"2026-13-50"` → 유효하지 않음

---

```python
import re
```

## 설명
정규표현식(regular expression)을 사용하기 위해 import합니다.

여기서는 날짜 형식이  
`YYYY-MM-DD`  
처럼 생겼는지 먼저 검사할 때 사용합니다.

---

# 3. `EnergyDataCreate` 클래스

```python
class EnergyDataCreate(BaseModel):
```

## 설명
새로운 에너지 데이터를 **생성(create)** 할 때 사용하는 요청 모델입니다.

예를 들어 프론트엔드에서 이런 데이터를 보낼 때 사용됩니다:

```json
{
  "date": "2026-09-01",
  "value": 4.52,
  "memo": "Worked from home, AC running"
}
```

`BaseModel`을 상속하므로 자동 검증이 됩니다.

---

## 3-1. `date` 필드

```python
date: str = Field(..., description="Local calendar date in YYYY-MM-DD format", example="2026-09-01")
```

## 설명
- `date`라는 필드는 문자열(`str`)이어야 합니다.
- `Field(...)`에서 `...`는 **필수값(required)** 이라는 뜻입니다.

### 세부 의미
- `date: str` → 문자열 타입
- `Field(...)` → 반드시 있어야 함
- `description=...` → Swagger/OpenAPI 문서 설명
- `example="2026-09-01"` → 예시값

즉:
- 요청에 `date`가 빠지면 에러
- 문자열이어야 함
- 형식은 아래 validator에서 추가 검사함

---

## 3-2. `value` 필드

```python
value: float = Field(..., ge=0.0, description="Daily electricity consumption in kWh", example=4.52)
```

## 설명
하루 전력 사용량입니다.

### 세부 의미
- `float` → 실수값
- `Field(...)` → 필수값
- `ge=0.0` → **0 이상이어야 함**
  - `ge`는 greater than or equal
- 음수 전력 사용량은 허용하지 않음

예:
- `4.52` → 가능
- `0.0` → 가능
- `-3.0` → 불가능

---

## 3-3. `memo` 필드

```python
memo: Optional[str] = Field(default=None, max_length=500, description="Optional user note", example="Worked from home, AC running")
```

## 설명
사용자가 남길 수 있는 메모입니다.

### 세부 의미
- `Optional[str]` → 문자열이거나 `None`
- `default=None` → 기본값은 없음
- 즉, 보내지 않아도 됨
- `max_length=500` → 최대 500자

예:
- `"에어컨 오래 사용"` → 가능
- 없음 → 가능
- 500자 초과 → 에러

---

## 3-4. `estimated_cost_pence` 필드

```python
estimated_cost_pence: Optional[float] = Field(default=None, ge=0.0, description="Optional estimated daily cost in pence")
```

## 설명
하루 전기 사용량에 대한 **예상 비용(펜스 단위)** 입니다.

### 세부 의미
- 선택값
- 실수 또는 `None`
- 0 이상만 허용

예:
- `125.5` → 125.5 pence
- 없음 → 가능
- `-10` → 불가능

---

## 3-5. `standing_charge_pence` 필드

```python
standing_charge_pence: Optional[float] = Field(default=None, ge=0.0, description="Optional standing charge in pence")
```

## 설명
기본요금(standing charge)을 펜스 단위로 저장합니다.

### 세부 의미
- 선택값
- 0 이상
- 없을 수도 있음

---

# 4. 날짜 검증기

```python
    @field_validator("date")
```

## 설명
이 데코레이터는 아래 함수가 `date` 필드를 검증한다는 뜻입니다.

즉,
- `date` 값이 들어오면
- 아래 함수 `validate_date_format()`가 실행됩니다.

---

```python
    @classmethod
```

## 설명
이 메서드를 클래스 메서드로 정의합니다.

Pydantic validator에서 자주 쓰는 형태입니다.

---

```python
    def validate_date_format(cls, v: str) -> str:
```

## 설명
`date` 값을 검사하는 함수입니다.

### 파라미터
- `cls` → 클래스 자체
- `v: str` → 들어온 date 값

### 반환값
- 검증 통과한 문자열 반환

즉:
- 이상 없으면 `v`를 그대로 돌려줌
- 문제가 있으면 `ValueError` 발생

---

```python
        pattern = r"^\d{4}-\d{2}-\d{2}$"
```

## 설명
날짜 형식을 검사하기 위한 정규표현식 패턴입니다.

의미:
- `^` → 문자열 시작
- `\d{4}` → 숫자 4개 (연도)
- `-` → 하이픈 hyphen
- `\d{2}` → 숫자 2개 (월)
- `-` → 하이픈 hyphen
- `\d{2}` → 숫자 2개 (일)
- `$` → 문자열 끝

즉 `"2026-09-01"` 같은 형태만 허용합니다.

허용:
- `2026-09-01`

불허:
- `2026/09/01`
- `26-09-01`
- `2026-9-1`

---

```python
        if not re.match(pattern, v):
```

## 설명
입력된 `v`가 위 패턴과 맞지 않으면 실행됩니다.

즉, 형식이 `YYYY-MM-DD`가 아니면 실패입니다.

---

```python
            raise ValueError("Date must be in YYYY-MM-DD format")
```

## 설명
형식이 틀리면 에러를 발생시킵니다.

예:
- `"2026/09/01"` 입력 시 이 에러 발생

FastAPI에서는 이런 에러를 자동으로 잡아서  
422 Validation Error 응답으로 바꿔줍니다.

---

```python
        try:
            datetime.strptime(v, "%Y-%m-%d")
```

## 설명
정규식으로는 “모양”만 검사합니다.  
하지만 `"2026-99-99"`처럼 모양은 맞아도 실제 날짜는 틀릴 수 있죠.

그래서 `datetime.strptime()`로  
**실제로 달력상 유효한 날짜인지** 검사합니다.

예:
- `"2026-09-01"` → 통과
- `"2026-02-30"` → 실패
- `"2026-13-01"` → 실패

---

```python
        except ValueError:
            raise ValueError("Invalid calendar date")
```

## 설명
`strptime`이 실패하면, 즉 유효하지 않은 날짜면 에러를 냅니다.

형식은 맞지만 실제 존재하지 않는 날짜일 때 이 메시지가 나옵니다.

---

```python
        return v
```

## 설명
검증이 모두 통과했으면 원래 값을 그대로 반환합니다.

즉:
- 형식 OK
- 실제 날짜 OK
- 그러면 사용 가능

---

# 5. `EnergyDataUpdate` 클래스

```python
class EnergyDataUpdate(BaseModel):
```

## 설명
기존 데이터를 **수정(update)** 할 때 사용하는 모델입니다.

생성 모델과의 가장 큰 차이점은:
- **모든 필드가 선택값(Optional)** 이라는 점입니다.

왜냐하면 수정은 일부만 바꿀 수도 있기 때문입니다.

예:
- 메모만 수정
- value만 수정
- 비용만 수정

---

## 5-1. `value`

```python
value: Optional[float] = Field(default=None, ge=0.0, description="Daily electricity consumption in kWh", example=5.10)
```

## 설명
- 수정할 전력 사용량
- 선택값
- 넣으면 0 이상이어야 함

즉:
- 안 보내면 수정 안 함
- 보내면 유효성 검사함

---

## 5-2. `memo`

```python
memo: Optional[str] = Field(default=None, max_length=500, description="Optional user note", example="Updated note")
```

## 설명
- 수정할 메모
- 선택값
- 최대 500자

---

## 5-3. `estimated_cost_pence`

```python
estimated_cost_pence: Optional[float] = Field(default=None, ge=0.0, description="Optional estimated daily cost in pence")
```

## 설명
- 예상 비용 수정용 필드
- 선택값
- 0 이상

---

## 5-4. `standing_charge_pence`

```python
standing_charge_pence: Optional[float] = Field(default=None, ge=0.0, description="Optional standing charge in pence")
```

## 설명
- 기본요금 수정용 필드
- 선택값
- 0 이상

---

# 6. `EnergyDataResponse` 클래스

```python
class EnergyDataResponse(BaseModel):
```

## 설명
이 모델은 **하나의 에너지 데이터 레코드를 API 응답으로 보낼 때** 사용합니다.

즉, 클라이언트가 받는 “완성된 한 건의 데이터” 형식입니다.

---

## 6-1. `id`

```python
id: str = Field(..., description="Unique document ID (local date string YYYY-MM-DD)")
```

## 설명
각 문서의 고유 ID입니다.

여기서는 설명상  
`YYYY-MM-DD` 형식의 날짜 문자열을 ID로 사용하는 것으로 보입니다.

즉:
- `"2026-09-01"` 자체가 문서 ID일 가능성이 큼

---

## 6-2. `date`

```python
date: str = Field(..., description="Local calendar date in YYYY-MM-DD format")
```

## 설명
기록 날짜입니다.

응답에도 날짜를 별도로 포함합니다.

---

## 6-3. `value`

```python
value: float = Field(..., description="Daily electricity consumption in kWh")
```

## 설명
하루 전기 사용량입니다.

응답에서는 이미 저장된 값이므로 필수입니다.

---

## 6-4. `unit`

```python
unit: str = Field(default="kWh", description="Energy unit")
```

## 설명
단위입니다.

기본값이 `"kWh"`로 정해져 있습니다.

즉, 응답에 별도로 단위를 넣어서  
프론트엔드가 헷갈리지 않도록 합니다.

---

## 6-5. `memo`

```python
memo: Optional[str] = Field(default=None, description="Optional user note")
```

## 설명
선택 메모입니다.

없으면 `None`일 수 있습니다.

---

## 6-6. `estimated_cost_pence`

```python
estimated_cost_pence: Optional[float] = Field(default=None, description="Estimated daily cost in pence (not actual bill)")
```

## 설명
예상 비용(펜스 단위)입니다.

괄호 속 설명이 중요합니다:
- 실제 청구서 금액이 아니라
- **추정치**임을 명확히 합니다

---

## 6-7. `estimated_cost_pounds`

```python
estimated_cost_pounds: Optional[float] = Field(default=None, description="Estimated daily cost in GBP (£)")
```

## 설명
예상 비용을 파운드 단위로도 제공합니다.

예:
- `estimated_cost_pence = 125.5`
- `estimated_cost_pounds = 1.255`

프론트엔드에서 계산하게 하지 않고  
백엔드가 미리 제공하는 구조일 수 있습니다.

---

## 6-8. `standing_charge_pence`

```python
standing_charge_pence: Optional[float] = Field(default=None, description="Standing charge in pence")
```

## 설명
기본요금입니다.

---

## 6-9. `created_at`

```python
created_at: Optional[str] = Field(default=None, description="ISO timestamp when created")
```

## 설명
데이터가 생성된 시각입니다.

보통 ISO 형식 문자열입니다.

예:
```python
"2026-09-01T12:34:56Z"
```

---

## 6-10. `updated_at`

```python
updated_at: Optional[str] = Field(default=None, description="ISO timestamp when updated")
```

## 설명
데이터가 마지막으로 수정된 시각입니다.

---

# 7. `EnergyDataListResponse` 클래스

```python
class EnergyDataListResponse(BaseModel):
```

## 설명
여러 개의 에너지 데이터를 한 번에 반환할 때 사용하는 응답 모델입니다.

예:
- 전체 목록 조회
- 기간별 조회

---

## 7-1. `total_count`

```python
total_count: int = Field(..., description="Total number of daily records in database")
```

## 설명
전체 레코드 개수입니다.

예:
- 데이터가 53개면 `total_count = 53`

프론트엔드에서 페이지 표시나 건수 표시할 때 유용합니다.

---

## 7-2. `records`

```python
records: List[EnergyDataResponse] = Field(..., description="List of daily energy records")
```

## 설명
실제 데이터 목록입니다.

### 타입 의미
- `List[...]` → 리스트
- `EnergyDataResponse` → 리스트 안 각 원소는 단일 응답 모델 형태

즉 이런 구조입니다:

```json
{
  "total_count": 2,
  "records": [
    {
      "id": "2026-09-01",
      "date": "2026-09-01",
      "value": 4.52,
      "unit": "kWh"
    },
    {
      "id": "2026-09-02",
      "date": "2026-09-02",
      "value": 5.10,
      "unit": "kWh"
    }
  ]
}
```

---

# 8. `SummaryResponse` 클래스

```python
class SummaryResponse(BaseModel):
```

## 설명
이 모델은 에너지 데이터의 **통계 요약 결과**를 응답할 때 사용합니다.

차트, 대시보드, AI 컨텍스트 등에 들어갈 수 있는  
큰 요약 구조라고 보면 됩니다.

---

## 8-1. `period`

```python
period: Dict[str, Any] = Field(..., description="Analysis period details")
```

## 설명
분석 기간 정보입니다.

예:
```python
{
  "start_date": "2026-09-01",
  "end_date": "202
```

---

# dict 가 아닌 class로 정의한 이유

네, **아주 중요한 질문**이에요 👍  
왜 굳이 `dict`가 아니라 **class(Pydantic 모델)** 로 정의했는지 이해하면 아키텍처가 훨씬 잘 보입니다.

한 줄로 먼저 말하면:

> `data_models.py`의 class들은 **데이터의 모양(구조)과 규칙을 표준화**하기 위해 존재합니다.

즉, 단순한 “객체 만들기”가 아니라 **입력/출력 데이터 계약서(schema)** 역할을 하는 거예요.

## 왜 class로 정의할까요?

### 1. 데이터 구조를 명확하게 만들기 위해
예를 들어 에너지 데이터 1건은 항상 이런 구조라고 약속하고 싶은 거예요:

```python
{
    "id": "2026-09-01",
    "date": "2026-09-01",
    "value": 4.52,
    "unit": "kWh",
    "memo": "Worked from home"
}
```

이걸 그냥 `dict`로만 쓰면:

- 어떤 키가 필요한지 헷갈릴 수 있고
- `value`가 문자열인지 숫자인지 불분명하고
- 누군가는 `datee`처럼 오타를 낼 수도 있어요

하지만 class로 만들면:

```python
class EnergyDataResponse(BaseModel):
    id: str
    date: str
    value: float
    unit: str = "kWh"
    memo: Optional[str] = None
```

이제 이 데이터는 **이런 필드들을 가져야 한다**고 명확해집니다.

---

### 2. 자동 검증(validation)을 하기 위해
이게 Pydantic class의 가장 큰 장점이에요.

예를 들어:

```python
EnergyDataCreate(
    date="2026-13-99",
    value=-10
)
```

이런 잘못된 데이터가 들어오면 class가 자동으로 검사해서 막아줍니다.

즉 class는 그냥 묶음이 아니라:

- 날짜 형식이 맞는지
- 음수인지 아닌지
- 필수값이 빠졌는지

를 **자동으로 검증하는 검사기** 역할도 해요.

---

### 3. `return`할 때 형식을 일정하게 유지하기 위해
사용자 질문하신 핵심이 여기예요.

`data_service.py`에서 return할 때 이런 식으로 쓸 수 있죠:

```python
return EnergyDataResponse(
    id=doc_id,
    date=data["date"],
    value=data["value"],
    memo=data.get("memo"),
    unit="kWh"
)
```

이렇게 하면 좋은 점이:

- 반환 데이터 형식이 항상 일정함
- 빠진 필드가 있으면 바로 알 수 있음
- 타입이 틀리면 자동 변환/검사 가능
- 다른 곳에서 이 return 값을 믿고 쓸 수 있음

즉, 서비스 함수가  
“아무 딕셔너리나 던지는 것”이 아니라  
**정해진 형식의 객체를 반환**하게 만드는 거예요.

---

# 왜 그냥 dict를 return하면 안 되나요?

할 수는 있습니다. 하지만 유지보수성이 떨어져요.

예를 들어 dict 방식:

```python
return {
    "id": doc_id,
    "date": data["date"],
    "value": data["value"]
}
```

이 방식의 문제:

- 키 이름 오타 위험
- 어떤 필드가 반드시 있어야 하는지 불명확
- 검증이 약함
- API 문서 자동화가 어려움
- 팀원이 구조를 추측해야 함

반면 class 방식:

```python
return EnergyDataResponse(
    id=doc_id,
    date=data["date"],
    value=data["value"]
)
```

이건 훨씬 명확하죠.

---

## 특히 FastAPI에서 class를 많이 쓰는 이유

FastAPI는 Pydantic 모델과 궁합이 매우 좋습니다.

### 예시 1: 요청 받을 때
```python
@router.post("/")
def create_data(payload: EnergyDataCreate):
    ...
```

의미:
- 클라이언트가 보내는 body는 `EnergyDataCreate` 형식이어야 함
- 틀리면 FastAPI가 자동으로 422 에러 반환

---

### 예시 2: 응답 줄 때
```python
@router.get("/{date}", response_model=EnergyDataResponse)
def get_data(date: str):
    ...
```

의미:
- 이 API의 응답은 `EnergyDataResponse` 구조여야 함
- Swagger 문서도 자동 생성됨
- 응답 형식이 표준화됨

즉, class 하나 정의해두면:

- 입력 검증
- 출력 표준화
- API 문서화

를 한 번에 얻습니다.

---

## data_service.py에서 왜 이 class를 return하나요?

서비스 계층은 보통  
**원시 데이터(raw data)** 를  
**앱이 쓰기 좋은 형태의 객체** 로 바꿔주는 역할도 합니다.

예를 들어 DB에서 이런 데이터가 나왔다고 해볼게요:

```python
{
    "date": "2026-09-01",
    "value": 4.52,
    "memo": "Worked from home",
    "created_at": "2026-09-01T12:00:00Z"
}
```

서비스는 이걸 그냥 넘기지 않고:

```python
return EnergyDataResponse(
    id="2026-09-01",
    date="2026-09-01",
    value=4.52,
    memo="Worked from home",
    unit="kWh",
    created_at="2026-09-01T12:00:00Z"
)
```

이렇게 **정리된 응답 객체**로 바꿔줍니다.

즉, 서비스는
- DB 형식
- 비즈니스 로직 형식
- API 응답 형식

사이를 연결하는 중간 정리자 역할을 해요.

---

## class를 쓰면 좋은 점 정리

1. 구조가 명확함: 무슨 필드가 있는지 한눈에 보임
2. 검증 가능: 잘못된 데이터를 자동으로 막음
3. 재사용 가능: 여러 함수/라우터에서 같은 모델을 공유 가능
4. 자동 문서화: FastAPI Swagger 문서가 예쁘게 생성됨
5. IDE 도움: 자동완성, 타입 추적이 쉬워짐
6. 협업에 유리: 팀원이 “이 API가 어떤 형식인지” 바로 이해 가능

---

# 비유로 이해해보면

## dict 방식
메모지에 자유롭게 적는 것

- 빠르긴 함
- 하지만 형식이 제각각일 수 있음

## Pydantic class 방식
정해진 양식의 신청서

- 이름 칸
- 날짜 칸
- 숫자 칸
- 틀리면 제출 불가

즉, class는 **정해진 양식**이에요.

---

# 그럼 이 class는 “객체지향의 class”와 같은 건가요?

완전히 같은 느낌은 아니고,  
여기서는 주로 **데이터 스키마 class**로 쓰입니다.

즉:

- 복잡한 동작(method)을 많이 넣는 class라기보다
- **데이터 구조를 정의하는 class**

에 더 가깝습니다.

예를 들어 `EnergyDataResponse`는
“무언가를 행동하는 객체”라기보다

> “이런 모양의 데이터를 나타내는 타입”

이라고 보는 게 더 정확해요.

---

# 결론

`data_models.py`의 class들은 단순히 묶어놓은 게 아니라,

> **입력/출력 데이터의 형식, 검증 규칙, 문서화, 재사용성을 담당하는 표준 모델**

입니다.

그리고 `data_service.py`에서 그걸 `return`하는 이유는,

> 서비스가 항상 **일정하고 검증된 형태의 데이터**를 넘기게 만들기 위해서예요.

---

원하시면 다음엔 제가 이어서

1. **`data_service.py`에서 실제로 이 모델들이 어떻게 return되는지**  
2. **dict 반환 vs Pydantic 반환 차이**  
3. **router의 `response_model`과 연결되는 흐름**

--------------------------------------------------------------------------------------------

좋아요! 이 부분 이해하면 **FastAPI 백엔드 흐름이 한 번에 정리**됩니다 😊

질문하신 핵심:

> `router`의 `response_model`이  
> `data_service.py`에서 return하는 Pydantic class와  
> **어떻게 연결되는가?**

---

# 먼저 한 줄 요약

`response_model`은

> **"이 라우터의 최종 응답은 이 형태여야 해"**  
> 라고 FastAPI에 알려주는 약속입니다.

그리고 서비스 함수가 `EnergyDataResponse` 같은 모델을 반환하면,  
FastAPI가 그걸 받아서:

1. **검증하고**
2. **JSON으로 바꾸고**
3. **문서화(Swagger)까지 자동 처리**합니다.

---

# 전체 흐름 먼저 보기

보통 구조는 이렇게 됩니다:

(app/routers/data.py)
```python
# router
@router.get("/{date}", response_model=EnergyDataResponse)
def get_energy_data(date: str):
    return data_service.get_data_by_date(date)
```

```python
# service
def get_data_by_date(date: str) -> EnergyDataResponse:
    raw = repository.get(date)
    return EnergyDataResponse(
        id=date,
        date=raw["date"],
        value=raw["value"],
        memo=raw.get("memo")
    )
```

---

# 흐름을 단계별로 보면

---

## 1단계: 클라이언트가 API 호출

예:

```http
GET /data/2026-09-01
```

브라우저나 프론트엔드가 서버에 요청합니다.

---

## 2단계: FastAPI가 router 함수 실행

```python
@router.get("/{date}", response_model=EnergyDataResponse)
def get_energy_data(date: str):
    return data_service.get_data_by_date(date)
```

여기서 FastAPI는 두 가지를 압니다:

- URL의 `{date}`를 함수 인자로 넣어야 한다
- 최종 응답 형식은 `EnergyDataResponse`여야 한다

즉 `response_model=EnergyDataResponse`는  
**응답 스키마 지정**입니다.

---

## 3단계: router가 service 호출

```python
return data_service.get_data_by_date(date)
```

라우터는 직접 DB를 다루지 않고, 서비스 계층에 일을 맡깁니다.

즉 router 역할은 주로:

- 요청 받기
- 파라미터 전달
- 서비스 호출
- 결과 반환

입니다.

---

## 4단계: service가 데이터 가공 후 return

예를 들어 DB에서 원시 데이터(raw data)를 가져왔다고 해볼게요.

```python
raw = {
    "date": "2026-09-01",
    "value": 4.52,
    "memo": "Worked from home"
}
```

서비스는 이걸 그냥 넘길 수도 있지만,  
보통 Pydantic 모델로 감싸서 반환합니다.

```python
return EnergyDataResponse(
    id="2026-09-01",
    date="2026-09-01",
    value=4.52,
    memo="Worked from home",
    unit="kWh"
)
```

이렇게 하면 서비스 단계에서 이미:

- 데이터 구조를 정리하고
- 필요한 필드를 맞추고
- 타입을 명확히 할 수 있습니다

---

## 5단계: router가 받은 값을 FastAPI가 `response_model`로 확인

이게 핵심입니다.

라우터가 반환한 값이 있으면,  
FastAPI는 그 값을 그냥 바로 JSON으로 보내지 않고

```python
response_model=EnergyDataResponse
```

이 규칙에 맞는지 한 번 더 봅니다.

즉 내부적으로는 이런 느낌이에요:

> "네가 반환한 값이 `EnergyDataResponse` 형태 맞아?"

---

# 여기서 가능한 경우 3가지

---

## 경우 1: service가 이미 `EnergyDataResponse`를 반환한 경우

```python
return EnergyDataResponse(...)
```

이 경우 가장 깔끔합니다.

왜냐하면 이미 서비스에서 한 번 구조가 맞춰졌기 때문이에요.

FastAPI는 그 모델을 JSON 응답으로 바꿔줍니다.

결과:

```json
{
  "id": "2026-09-01",
  "date": "2026-09-01",
  "value": 4.52,
  "unit": "kWh",
  "memo": "Worked from home"
}
```

---

## 경우 2: service가 `dict`를 반환한 경우

```python
return {
    "id": "2026-09-01",
    "date": "2026-09-01",
    "value": 4.52,
    "unit": "kWh",
    "memo": "Worked from home"
}
```

이것도 가능합니다.

왜냐하면 FastAPI가 `response_model=EnergyDataResponse`를 보고  
그 dict를 **EnergyDataResponse 형태로 검증/변환**하려 하기 때문입니다.

즉:

- dict여도 가능
- 하지만 최종적으로는 `response_model` 기준으로 맞춰짐

---

## 경우 3: 잘못된 구조를 반환한 경우

예를 들어:

```python
return {
    "id": "2026-09-01",
    "date": "2026-09-01",
    "value": -999,   # 형식상 float는 맞지만 비즈니스상 이상할 수 있음
}
```

또는 더 심하게:

```python
return {
    "date": "2026-09-01"
}
```

이 경우 `response_model`이 요구하는 필드가 없으면  
FastAPI가 응답 검증 과정에서 문제를 발견할 수 있습니다.

즉 `response_model`은

> **"응답도 검증한다"**

는 의미가 있어요.

---

# `response_model`이 하는 일 3가지

---

## 1. 응답 형식 검증
반환값이 지정한 모델 구조와 맞는지 확인

---

## 2. 응답 필터링
이것도 매우 중요해요.

예를 들어 service가 이런 데이터를 반환했다고 합시다:

```python
return {
    "id": "2026-09-01",
    "date": "2026-09-01",
    "value": 4.52,
    "unit": "kWh",
    "memo": "Worked from home",
    "internal_debug": "secret",
    "db_password": "1234"
}
```

그런데 `response_model=EnergyDataResponse`에  
`internal_debug`, `db_password` 필드가 없다면?

FastAPI는 **모델에 없는 필드는 응답에서 제외**할 수 있습니다.

즉 `response_model`은  
**보내도 되는 데이터만 남기는 필터** 역할도 합니다.

이거 진짜 중요합니다.

---

## 3. Swagger/OpenAPI 문서 생성
`response_model`을 지정하면  
FastAPI 문서 페이지에서 응답 구조를 자동으로 보여줍니다.

예를 들어 Swagger에서:

- `id: string`
- `date: string`
- `value: number`
- `memo: string | null`

처럼 자동 문서가 생깁니다.

그래서 프론트엔드도 API 응답 모양을 쉽게 알 수 있어요.

---

# 코드 흐름 예시로 완전히 연결해서 보기

---

## 1. 모델 정의

```python
from pydantic import BaseModel
from typing import Optional

class EnergyDataResponse(BaseModel):
    id: str
    date: str
    value: float
    unit: str = "kWh"
    memo: Optional[str] = None
```

이건 “응답은 이런 모양이어야 함”이라는 스키마입니다.

---

## 2. service 함수

```python
def get_data_by_date(date: str) -> EnergyDataResponse:
    raw = {
        "date": date,
        "value": 4.52,
        "memo": "Worked from home"
    }

    return EnergyDataResponse(
        id=date,
        date=raw["date"],
        value=raw["value"],
        memo=raw.get("memo")
    )
```

서비스는 DB/raw 데이터를  
API용 응답 모델로 변환합니다.

---

## 3. router 함수

```python
@router.get("/{date}", response_model=EnergyDataResponse)
def get_energy_data(date: str):
    return data_service.get_data_by_date(date)
```

여기서 router는 service 결과를 그대로 반환합니다.

---

## 4. FastAPI 처리

FastAPI는 반환값을 받아:

- `EnergyDataResponse` 형태인지 확인
- JSON 직렬화
- 클라이언트에게 응답

합니다.

---

## 5. 최종 응답

```json
{
  "id": "2026-09-01",
  "date": "2026-09-01",
  "value": 4.52,
  "unit": "kWh",
  "memo": "Worked from home"
}
```

---

# 자주 헷갈리는 포인트

---

## `return EnergyDataResponse(...)` 했으면 `response_model` 없어도 되나요?

기술적으로는 응답은 나갈 수 있습니다.  
하지만 **보통 `response_model`도 같이 쓰는 게 좋습니다.**

이유:

- 문서화됨
- 응답 필터링 가능
- 라우터 수준에서 계약이 명확해짐

즉,

- service return 타입 힌트 → Python 개발자용
- router `response_model` → FastAPI/문서/API 계약용

이라고 보면 됩니다.

---

## 서비스에서 이미 모델로 return하는데 왜 또 `response_model`이 필요하죠?

좋은 질문입니다.

둘은 비슷해 보이지만 역할이 조금 달라요.

### 서비스의 Pydantic 반환
- 내부 코드 품질
- 타입 명확화
- 비즈니스 계층 정리

### router의 `response_model`
- 외부 API 계약
- 응답 검증
- 문서화
- 필터링

즉, 서비스와 라우터에서 **각자 다른 층에서 안전장치**를 두는 거예요.

---

# 비유로 이해하기

---

## service
요리를 만드는 주방

- 재료(DB 데이터)를 가져와서
- 예쁘게 요리(응답 객체)해서 내놓음

## router
서빙 직원

- 손님 요청 받음
- 주방에 전달
- 나온 요리를 손님에게 전달

## `response_model`
메뉴판 사진 + 검수 기준

- 이 음식은 이런 모양이어야 함
- 이상한 재료가 섞이면 안 됨
- 손님에게 보여줄 설명도 됨

즉 `response_model`은  
**최종적으로 손님에게 나가는 결과물의 공식 기준**이에요.

---

# 실제 개발에서 권장 패턴

보통 이렇게 많이 씁니다:

```python
@router.get("/{date}", response_model=EnergyDataResponse)
def get_energy_data(date: str):
    return data_service.get_data_by_date(date)
```

```python
def get_data_by_date(date: str) -> EnergyDataResponse:
    raw = repository.get_by_date(date)
    return EnergyDataResponse(**raw)
```

또는 리스트면:

```python
@router.get("/", response_model=EnergyDataListResponse)
def list_energy_data():
    return data_service.list_data()
```

여기서 서비스는 `EnergyDataListResponse`를 반환합니다.

---

# 정리

`response_model`과 서비스 반환 흐름은 이렇게 연결됩니다:

1. **클라이언트가 요청**
2. **router가 요청 받음**
3. **router가 service 호출**
4. **service가 Pydantic 모델 또는 dict 반환**
5. **FastAPI가 `response_model` 기준으로 응답 검증/변환**
6. **JSON 응답 생성**
7. **Swagger 문서에도 같은 구조 반영**

---

# 핵심 한 문장

> `data_service.py`는 **응답 데이터를 만들어 주는 곳**이고,  
> `router`의 `response_model`은 **그 응답이 최종적으로 어떤 형태여야 하는지 보증하는 규칙**입니다.

---

원하시면 다음에는 이어서  
**실제 `data.py` 라우터 코드 기준으로**  
- `response_model=EnergyDataResponse`
- `response_model=EnergyDataListResponse`
- `response_model=SummaryResponse`

이 3개가 **각 엔드포인트에서 어떻게 쓰이는지**  
코드 흐름으로 바로 연결해서 설명해드릴게요.

---

# Pydantic model

**Imports**

* `from pydantic import BaseModel, Field, field_validator`: Imports core Pydantic components. `BaseModel` is the base class for data models, `Field` adds validation rules and OpenAPI schema metadata, and `@field_validator` defines custom validation logic for specific attributes.
* `from typing import Optional, List, Dict, Any`: Imports Python standard type hinting utilities (though only `Optional` is actively used here to allow `None` values).
* `from datetime import date, datetime`: Imports date and time tools from the standard library (`datetime` is used to verify real calendar dates).
* `import re`: Imports Python's built-in regular expression module to check string patterns.

**Class Definition & Fields**

* `class EnergyDataCreate(BaseModel):`: Defines a Pydantic data model named `EnergyDataCreate`, primarily used as a request body schema for creating a data entry.
* `date: str = Field(...)`: Declares a required `date` field as a string (`...` means required). It adds API documentation metadata: a description and an example string (`"2026-09-01"`).
* `value: float = Field(...)`: Declares a required `value` field as a float. `ge=0.0` ensures the value must be **g**reater than or **e**qual to `0.0` (disallowing negative energy usage).
* `memo: Optional[str] = Field(...)`: Declares an optional text field defaulting to `None`. `max_length=500` enforces a maximum length of 500 characters.

**Custom Validator**

* `@field_validator("date")`: A decorator that attaches the custom validation function directly below it to the `date` field.
* `@classmethod`: Decorates the validator method to operate at the class level (standard Pydantic v2 syntax).
* `def validate_date_format(cls, v: str) -> str:`: Defines the validator function taking the class (`cls`) and the incoming value (`v`) for the `date` field.
* `pattern = r"^\d{4}-\d{2}-\d{2}$"`: Sets a regex pattern enforcing exactly 4 digits, a hyphen, 2 digits, a hyphen, and 2 digits.
* `if not re.match(pattern, v):`: Checks if the string fits the structural shape of `YYYY-MM-DD`.
* `raise ValueError("Date must be in YYYY-MM-DD format")`: Rejects inputs like `"2026/09/01"` or `"September 1, 2026"`.
* `try:`: Begins a block to test if the string forms a valid calendar date.
* `datetime.strptime(v, "%Y-%m-%d")`: Attempts to parse the string into a real date object.
* `except ValueError:`: Catches parsing errors if the format matches the regex but represents an impossible date.
* `raise ValueError("Invalid calendar date")`: Rejects logically impossible dates like `"2026-02-31"` or `"2026-13-45"`.
* `return v`: Returns the original string unchanged if all validations pass.


요청하신 추가 코드(업데이트, 응답, 목록, 요약 통계 모델)의 라인별 설명입니다.

**1. EnergyDataUpdate (기존 데이터 수정용 모델)**

* `class EnergyDataUpdate(BaseModel):`: 부분 업데이트(PATCH 요청 등)를 위해 일부 필드만 선택적으로 받을 수 있는 Pydantic 모델을 정의합니다.
* `value: Optional[float] = Field(...)`: 수정할 전력 사용량(kWh) 필드입니다. `Optional[float]`과 `default=None`으로 설정되어 있어 수정 시 이 필드를 생략할 수 있고, 입력할 경우 `ge=0.0` 제약조건에 의해 0 이상의 숫자만 허용합니다.
* `memo: Optional[str] = Field(...)`: 수정할 메모 필드입니다. 생략 가능하며(`default=None`), 입력할 경우 최대 500자까지 허용합니다.

---

**2. EnergyDataResponse (단일 기록 응답용 모델)**

* `class EnergyDataResponse(BaseModel):`: API가 클라이언트에게 단일 에너지 사용량 기록을 반환할 때 사용하는 응답 구조 모델입니다.
* `id: str = Field(...)`: 데이터베이스의 레코드 고유 식별자(UUID 또는 날짜 문자열 등)입니다. 필수 값입니다.
* `date: str = Field(...)`: 해당 사용량의 날짜(`YYYY-MM-DD` 형식)입니다. 필수 값입니다.
* `value: float = Field(...)`: 전력 사용량 수치입니다. 필수 값입니다.
* `unit: str = Field(default="kWh", ...)`: 에너지 단위 필드로, 기본값이 `"kWh"`로 자동 설정됩니다.
* `memo: Optional[str] = Field(...)`: 기록된 사용자 메모입니다. 메모가 없을 경우 `None`(null)을 반환합니다.
* `created_at: Optional[str] = Field(...)`: 해당 레코드가 생성된 시각(ISO timestamp 형식)입니다.
* `updated_at: Optional[str] = Field(...)`: 해당 레코드가 마지막으로 수정된 시각(ISO timestamp 형식)입니다.

---

**3. EnergyDataListResponse (목록 조회 응답용 모델)**

* `class EnergyDataListResponse(BaseModel):`: 여러 개의 에너지 기록과 전체 개수를 함께 반환하는 페이징/목록 응답 모델입니다.
* `total_count: int = Field(...)`: 조건에 해당하는 전체 레코드의 총 개수(정수)입니다.
* `records: List[EnergyDataResponse] = Field(...)`: 앞서 정의한 `EnergyDataResponse` 객체들이 담긴 리스트(배열)입니다.

---

**4. SummaryResponse (통계 분석 응답용 모델)**

* `class SummaryResponse(BaseModel):`: 종합 분석 데이터를 대시보드 등에 전달하기 위한 상세 통계 응답 모델입니다.
* `period: Dict[str, Any] = Field(...)`: 분석 대상 기간 정보(예: 시작일, 종료일)를 담는 키-값 구조의 Dict입니다.
* `counts: Dict[str, Any] = Field(...)`: 데이터 수집 일수, 누락 일수 등의 개수 정보를 담은 Dict입니다.
* `overall: Dict[str, Any] = Field(...)`: 전체 기간의 총 사용량, 평균 사용량 등 종합 통계를 담은 Dict입니다.
* `extremes: Dict[str, Any] = Field(...)`: 최고/최저 사용량을 기록한 날짜와 수치 정보를 담은 Dict입니다.
* `monthly: Dict[str, Any] = Field(...)`: 월별 합계 및 월별 평균 사용량을 담은 Dict입니다.
* `weekday_weekend: Dict[str, Any] = Field(...)`: 평일 vs 주말 사용량 비교 분석 데이터를 담은 Dict입니다.
* `day_of_week: Dict[str, Any] = Field(...)`: 요일별(월~일) 평균 사용량 데이터를 담은 Dict입니다.
* `recent: Dict[str, Any] = Field(...)`: 최근 7일, 30일간의 단기 지표 데이터를 담은 Dict입니다.
* `trend: Dict[str, Any] = Field(...)`: 사용량 증가/감소 추세를 분석한 데이터를 담은 Dict입니다.
* `cost: Optional[Dict[str, Any]] = Field(...)`: 추정 전기 요금 통계 정보를 담는 Dict입니다. 계산 모듈이 없거나 설정되지 않은 경우 `None`을 반환합니다.