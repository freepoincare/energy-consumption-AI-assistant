# 정의

* API: 서로 다른 프로그램이나 서비스가 데이터를 주고받을 수 있도록 정해진 통신 규칙.
* HTTP: 웹 브라우저와 서버가 데이터를 요청하고 응답할 때 사용하는 통신 규칙(프로토콜)입니다.
* API vs. HTTP: API는 프로그램 간에 데이터를 주고받는 방법/규칙이고, HTTP는 그 데이터를 웹에서 주고받기 위해 사용하는 통신 프로토콜
* GET / POST / PUT / DELETE: HTTP에서 사용하는 주요 요청 방식으로, 각각 데이터 조회(GET), 생성(POST), 수정(PUT), 삭제(DELETE)에 사용.
* CRUD: 데이터를 다루는 기본 기능인 생성(Create), 조회(Read), 수정(Update), 삭제(Delete)를 의미.
* REST API: HTTP의 URL과 요청 방식을 활용하여 자원(Resource)을 일관된 방식으로 주고받도록 설계한 API 구조.
* JSON: 서버와 클라이언트 사이에서 데이터를 구조화하여 주고받기 위해 사용하는 가벼운 텍스트 데이터 형식.
* FastAPI: Python으로 빠르고 간편하게 REST API 서버를 만들 수 있도록 도와주는 웹 프레임워크.
* REST API: HTTP의 GET, POST, PUT, DELETE 같은 요청 방식을 활용해 웹의 자원(Resource)을 일관된 규칙으로 주고받도록 설계한 API.
* Endpoint: 클라이언트가 실제로 호출하는 구체적인 주소/접점; 외부에서 보는 API 주소
* Route: 서버가 요청을 어떻게 연결할지 정한 규칙; 주소를 처리하는 서버의 매핑 규칙
* Pydantic: Python에서 데이터의 형식과 유효성을 자동으로 검사하고 관리할 수 있도록 도와주는 라이브러리. 파이썬 생태계의 핵심 데이터 유효성 검사 도구. 데이터 검증. API 요청/응답 검증에도 사용. 외부의 신뢰할 수 없는 데이터(API 요청, DB 결과, AI 생성 텍스트 등)를 신뢰할 수 있는 파이썬 객체로 맵핑. 데이터 품질 높임.
* Swagger UI: 개발자가 작성한 API(REST API)의 구조를 웹 브라우저에서 시각적으로 보여주고, 직접 테스트할 수 있도록 도와주는 오픈소스 인터페이스 툴
* Firestore: Google Cloud에서 제공하는 NoSQL 데이터베이스로, 애플리케이션 데이터를 문서(Document)와 컬렉션(Collection) 형태로 저장.
* Environment variable: API 키나 비밀번호처럼 코드에 직접 노출하면 안 되는 설정 값을 프로그램 외부에서 관리하기 위한 환경 변수.
* CORS: 다른 출처(Origin)의 웹 페이지가 서버의 API에 접근할 수 있도록 허용하거나 제한하는 보안 정책.
* uvicorn: 서버를 실행하는 프로그램 이름; 서버 엔진; FastAPI 같은 현대적인 파이썬 웹 애플리케이션을 구동하는 빠른 웹 서버(ASGI 서버)
* OpenAI API: 애플리케이션에서 OpenAI의 AI 모델을 호출하여 텍스트 생성, 분석 등의 기능을 사용할 수 있도록 제공되는 API.
* System prompt: AI의 역할, 행동 방식, 답변 규칙 등을 미리 지정하여 모델의 기본적인 응답 방식을 설정하는 프롬프트.
* Context injection: 사용자의 질문과 함께 관련 데이터나 정보를 AI에게 전달하여 더 정확하고 상황에 맞는 답변을 생성하도록 하는 방식.
* Function Calling: AI가 필요에 따라 미리 정의된 함수를 호출하여 외부 데이터 조회나 특정 작업을 자동으로 실행하도록 하는 기능.
* Conversation history: 사용자와 AI가 이전에 주고받은 메시지를 저장하고 다시 전달하여 대화의 맥락을 유지하는 기능.

---

* CORS(Cross-Origin Resource Sharing) 설정: 보안상의 이유로 브라우저는 다른 도메인(Origin)에서 오는 API 요청을 기본적으로 차단합니다. 예를 들어, 프론트엔드(http://localhost:3000)가 백엔드(http://localhost:8000)에 데이터를 요청하려면 백엔드에서 "이 도메인의 접근을 허용하겠다"고 명시해야 합니다. 이를 처리해 주는 설정입니다.

---

# 1. 시계열 데이터 분석 및 요약 정보 활용

시계열 데이터를 분석하고, 요약 정보를 만들어 서비스에서 활용하는 흐름을 설명하라.

30분 단위로 수집된 전력 사용량 데이터를 날짜별로 집계하여 일별 소비량(kWh/day)으로 변환하고, 이를 기반으로 시계열 데이터를 분석함. 전체 평균, 최대·최소 사용량, 월별 사용량, 평일·주말 차이, 최근 7일 및 30일의 소비 패턴 등을 계산하여 구조화된 요약 정보를 생성함. 또한 7일 이동평균을 활용하여 일별 변동을 완화하고 단기적인 소비 추세를 파악할 수 있도록 구성함. 이렇게 생성된 요약 정보는 이후 AI가 사용자의 전력 사용량 관련 질문에 답변할 때 활용됨.

서비스 흐름:
```text
Firestore에서 데이터 조회
   ↓
데이터 정제/검증
   ↓
날짜순 정렬
   ↓
통계/추세 분석
   ↓
요약 정보 생성
   ↓
서비스에서 활용
   ├─ 차트 API
   ├─ 대시보드 요약 카드
   ├─ AI 시스템 프롬프트 주입
   └─ 이상치/인사이트 메시지
```

---

<details>
<summary>[상세 설명]</summary>
<br>

이건 에너지관리 앱에서 **데이터 → 분석 → 요약 → 서비스 활용**으로 이어지는 핵심 흐름이에요.

한 줄로 먼저 말하면:

> **시계열 데이터 분석 흐름**은  
> 날짜순 데이터들을 모아서 → 정리하고 → 통계/추세를 계산한 뒤 →  
> 그 결과를 **차트, API 응답, AI 컨텍스트, 인사이트 메시지**에 활용하는 과정입니다.

---

## 1. 시계열 데이터가 뭐예요?

시계열 데이터는 **시간 순서가 있는 데이터**예요.

예:
```python
[
    {"date": "2026-09-01", "value": 4.2},
    {"date": "2026-09-02", "value": 4.8},
    {"date": "2026-09-03", "value": 5.1},
]
```

에너지 앱에서는 보통:

- 날짜별 전력 사용량
- 시간대별 사용량
- 주간/월간 기록

이런 것들이 시계열 데이터입니다.

---

## 2. 전체 흐름 먼저 보기

보통 서비스 흐름은 이렇게 됩니다:

```text
Firestore에서 데이터 조회
   ↓
데이터 정제/검증
   ↓
날짜순 정렬
   ↓
통계/추세 분석
   ↓
요약 정보 생성
   ↓
서비스에서 활용
   ├─ 차트 API
   ├─ 대시보드 요약 카드
   ├─ AI 시스템 프롬프트 주입
   └─ 이상치/인사이트 메시지
```

---

## 3. 1단계: 원본 시계열 데이터 조회

예를 들어 Firestore에서 에너지 기록을 가져옵니다.

```python
docs = db.collection("energy_data").stream()

records = []
for doc in docs:
    data = doc.to_dict()
    records.append(data)
```

#### 여기서 하는 일
- DB에서 raw data 가져오기
- 아직은 그냥 원본 상태

---

## 4. 2단계: 데이터 정제 / 검증

DB 데이터는 바로 분석하지 않고 먼저 정리하는 게 좋아요.

예:
- 날짜 형식이 올바른지
- value가 숫자인지
- 빠진 필드가 없는지
- 중복이 있는지

예시:

```python
from datetime import datetime

cleaned = []

for item in records:
    if "date" not in item or "value" not in item:
        continue

    cleaned.append({
        "date": datetime.fromisoformat(item["date"]),
        "value": float(item["value"])
    })
```

#### 왜 필요하나요?
분석은 숫자와 날짜가 정확해야 하니까요.  
정제가 안 되면 평균, 추세 계산이 틀어질 수 있어요.

---

## 5. 3단계: 날짜순 정렬

시계열 데이터는 **순서**가 중요합니다.

```python
cleaned.sort(key=lambda x: x["date"])
```

#### 왜 중요하나요?
그래야:
- 최근 7일 계산 가능
- 증가/감소 추세 판단 가능
- 차트 x축이 올바르게 나옴

---

## 6. 4단계: 기본 통계 계산

이제 분석을 시작합니다.

보통 많이 계산하는 것:

- 총 기록 수
- 평균 사용량
- 합계
- 최대값 / 최소값
- 최고 사용일 / 최저 사용일

예시:

```python
values = [item["value"] for item in cleaned]

count = len(values)
total = sum(values)
avg = total / count if count else 0
max_item = max(cleaned, key=lambda x: x["value"]) if cleaned else None
min_item = min(cleaned, key=lambda x: x["value"]) if cleaned else None
```

---

## 7. 5단계: 최근 구간 분석

시계열 데이터에서는 **전체 평균**만 보면 부족하고, **최근 변화**가 중요해요.

예:
- 최근 7일 평균
- 최근 30일 평균
- 이전 7일과 비교
- 최근 증가/감소 추세

```python
recent_7 = cleaned[-7:]
recent_values = [item["value"] for item in recent_7]
recent_avg = sum(recent_values) / len(recent_values) if recent_values else 0
```

---

## 8. 6단계: 추세(trend) 판단

예를 들어:

- 최근 평균이 전체 평균보다 높으면 증가 경향
- 최근 평균이 낮으면 감소 경향
- 차이가 작으면 안정적

```python
if recent_avg > avg + 0.3:
    trend = "increasing"
elif recent_avg < avg - 0.3:
    trend = "decreasing"
else:
    trend = "stable"
```

#### 설명
이건 아주 단순한 예시지만, 서비스에서는 이런 식으로 “상태 라벨”을 만들 수 있어요.

예:
- `increasing`
- `decreasing`
- `stable`

---

## 9. 7단계: 요약 정보(summary) 만들기

이제 계산 결과를 서비스에서 쓰기 좋은 형태로 묶습니다.

```python
summary = {
    "count": count,
    "total": total,
    "average": round(avg, 2),
    "recent_7d_average": round(recent_avg, 2),
    "trend": trend,
    "max_value": max_item["value"] if max_item else None,
    "max_date": max_item["date"].date().isoformat() if max_item else None,
    "min_value": min_item["value"] if min_item else None,
    "min_date": min_item["date"].date().isoformat() if min_item else None,
}
```

이 summary는 아주 중요해요.

왜냐하면 raw data 전체를 매번 쓰기보다, **이미 분석된 핵심 결과만 재사용**할 수 있기 때문입니다.

---

## 10. 8단계: 서비스 계층에서 반환

`data_service.py` 같은 곳에서는 이런 summary를 API나 AI에서 쓰도록 반환합니다.

예:

```python
def get_energy_summary():
    records = load_energy_data()
    cleaned = clean_and_sort(records)
    summary = analyze_time_series(cleaned)
    return summary
```

즉 서비스 계층은:

- DB 조회
- 분석 호출
- 결과 반환

을 담당합니다.

---

## 11. 이 요약 정보를 어디에 쓰나요?

이제 핵심이에요. summary는 여러 곳에서 재활용됩니다.

---

### 1) 대시보드 카드
예:
- 평균 사용량
- 최고 사용일
- 최근 추세

프론트에서 이렇게 표시 가능:

```json
{
  "average": 4.25,
  "trend": "increasing",
  "max_date": "2026-09-03"
}
```

---

### 2) 차트 데이터 보조 설명
차트만 보여주면 사용자가 해석하기 어려울 수 있어요.

그래서:
- “최근 사용량이 증가 중입니다”
- “최고 사용량은 9월 3일입니다”

같은 설명을 같이 붙입니다.

---

### 3) AI 컨텍스트 주입
이전 질문과 연결되죠.

summary를 텍스트로 바꿔서 시스템 프롬프트에 넣습니다.

예:
```python
context_text = f"""
현재 사용자 에너지 요약:
- 총 기록 수: {summary['count']}
- 평균 사용량: {summary['average']} kWh
- 최근 7일 평균: {summary['recent_7d_average']} kWh
- 추세: {summary['trend']}
- 최고 사용일: {summary['max_date']} ({summary['max_value']} kWh)
"""
```

이렇게 하면 AI가 사용자 데이터 기반으로 답할 수 있어요.

---

### 4) 인사이트 / 경고 메시지
예:
- 최근 평균이 급증하면 절약 팁 제안
- 최고 사용일이 특정 패턴이면 알림

예:
```python
if summary["trend"] == "increasing":
    insight = "최근 사용량이 증가하고 있습니다. 냉방기기 사용 시간을 점검해보세요."
```

---

## 12. 함수 구조로 보면 더 이해 쉬워요

실제로는 보통 이렇게 나눕니다:

```python
def load_energy_data():
    # DB 조회
    pass

def clean_and_sort(records):
    # 날짜 변환, 숫자 변환, 정렬
    pass

def analyze_time_series(records):
    # 평균, 최대/최소, 최근 평균, 추세 계산
    pass

def build_summary_text(summary):
    # AI 주입용 텍스트 생성
    pass
```

#### 장점
- 역할이 분리됨
- 테스트 쉬움
- 나중에 분석 로직만 바꾸기 쉬움

---

## 13. 간단한 전체 예시

```python
from datetime import datetime

def clean_and_sort(records):
    cleaned = []

    for item in records:
        if "date" not in item or "value" not in item:
            continue

        cleaned.append({
            "date": datetime.fromisoformat(item["date"]),
            "value": float(item["value"])
        })

    cleaned.sort(key=lambda x: x["date"])
    return cleaned


def analyze_time_series(records):
    if not records:
        return {
            "count": 0,
            "average": 0,
            "recent_7d_average": 0,
            "trend": "no_data"
        }

    values = [r["value"] for r in records]
    avg = sum(values) / len(values)

    recent_7 = records[-7:]
    recent_values = [r["value"] for r in recent_7]
    recent_avg = sum(recent_values) / len(recent_values)

    max_item = max(records, key=lambda x: x["value"])
    min_item = min(records, key=lambda x: x["value"])

    if recent_avg > avg + 0.3:
        trend = "increasing"
    elif recent_avg < avg - 0.3:
        trend = "decreasing"
    else:
        trend = "stable"

    return {
        "count": len(records),
        "average": round(avg, 2),
        "recent_7d_average": round(recent_avg, 2),
        "trend": trend,
        "max_value": max_item["value"],
        "max_date": max_item["date"].date().isoformat(),
        "min_value": min_item["value"],
        "min_date": min_item["date"].date().isoformat(),
    }
```

#### 이 코드의 의미
- `clean_and_sort()` : 분석 전 준비
- `analyze_time_series()` : 실제 통계/추세 계산
- 반환된 summary는 API/AI/UI에서 재사용 가능

---

## 14. 실무에서 더 발전시키면

기초 분석 외에도 이런 걸 할 수 있어요:

- 이동평균(moving average)
- 전주 대비 / 전월 대비 변화율
- 이상치 탐지(outlier)
- 주중/주말 패턴 비교
- 계절성 분석

하지만 처음에는 지금처럼:

1. 정렬
2. 평균
3. 최근 평균
4. 최대/최소
5. 추세 요약

이 정도만 잘 이해해도 충분히 좋습니다 👍

---

## 15. 이 프로젝트 문맥에서 보면

당신이 배우고 있는 구조에 맞춰 보면:

#### `firestore.py`
- 원본 기록 저장소 접근

#### `data_service.py`
- 기록 조회
- 시계열 정리
- summary 생성

#### `app.js`
- 차트 렌더링
- 요약 카드 표시

#### `ai_service.py`
- summary를 시스템 프롬프트에 넣어 AI 답변 강화

즉:

> **data_service가 시계열 분석의 중심**이고,  
> 그 결과를 프론트와 AI가 함께 사용하는 구조예요.

---

## 16. 핵심 정리

### 흐름
1. DB에서 시간순 데이터 조회
2. 날짜/숫자 형식 정리
3. 날짜순 정렬
4. 평균, 합계, 최대/최소 계산
5. 최근 구간 분석
6. 추세 판단
7. summary 객체 생성
8. UI / API / AI에서 활용

### 요약 정보의 역할
- raw data를 바로 쓰지 않고
- **핵심만 압축한 재사용 가능한 정보**로 바꿔줌

---

## 17. 한 문장 결론

> **시계열 데이터 분석은 시간순 데이터를 정리한 뒤 평균·최근 변화·최대/최소 같은 특징을 추출하고, 그 결과를 summary로 만들어 대시보드·API·AI 서비스에서 공통으로 활용하는 과정**입니다.

---

<br>
</details>

---

# 2. FastAPI 프로젝트를 라우터/서비스 등으로 분리한 기준

FastAPI 프로젝트를 라우터/서비스 등으로 분리해 구성한 기준을 설명하라.

FastAPI 프로젝트는 API 요청을 처리하는 **Router**, 실제 비즈니스 로직을 담당하는 **Service**, 데이터 저장 및 조회를 담당하는 **Repository/Database Layer**로 역할을 분리함. Router에는 HTTP 요청과 응답 처리만 두고, 전력 사용량 분석이나 데이터 처리와 같은 핵심 로직은 Service에서 담당하도록 구성함. 이를 통해 각 기능의 책임을 명확하게 하고 코드의 재사용성과 유지보수성을 높일 수 있음. 또한 특정 데이터베이스나 외부 API가 변경되더라도 다른 계층에 미치는 영향을 최소화할 수 있도록 설계함.

---

<details>
<summary>[상세 설명]</summary>
<br>

FastAPI 프로젝트를 라우터/서비스 등으로 분리해 구성한 기준은 “파일을 예쁘게 나누기 위해서”가 아니라, 책임을 분리하기 위해서입니다.  

핵심 기준은 한마디로:

> **각 계층이 “무슨 책임”을 가지는지에 따라 분리**합니다.

즉 FastAPI 프로젝트를 나눌 때 기준은 **기능별**이 아니라 먼저 **역할별(책임별)** 입니다.

---

### 1. 왜 분리하나요?

처음엔 라우터 하나에 다 넣어도 됩니다.

```python
@router.post("/")
def create_data(payload: EnergyDataCreate):
    # 검증
    # DB 저장
    # 비용 계산
    # 응답 만들기
    ...
```

작을 때는 괜찮지만 커지면 문제가 생겨요.

- 라우터가 너무 길어짐
- 같은 로직이 여러 엔드포인트에 중복됨
- DB가 바뀌면 여기저기 수정해야 함
- 테스트가 어려움
- AI 기능, 통계 기능이 섞여 복잡해짐

그래서 보통 역할을 나눕니다.

---

### 2. 분리 기준의 핵심: “이 코드는 무슨 일을 하나?”

보통 이렇게 나눕니다.

---

#### ① Router 계층
**기준:** HTTP 요청/응답을 직접 다루는 코드인가?

여기에 들어가는 것:
- URL 경로
- `@router.get`, `@router.post`
- 요청 파라미터 받기
- `response_model`
- 상태코드
- 서비스 호출

예:
```python
@router.get("/{date}", response_model=EnergyDataResponse)
def get_energy_data(date: str):
    return data_service.get_data_by_date(date)
```

##### router의 책임
- 요청 받기
- 입력 전달하기
- 결과 반환하기

##### router가 하면 안 좋은 것
- 복잡한 계산
- 긴 비즈니스 규칙
- 직접 DB 쿼리
- 외부 API 처리 세부 구현

즉 router는 **입구/출구 담당**이에요.

---

#### ② Service 계층
**기준:** “이 앱에서 실제로 해야 하는 일/규칙”인가?

여기에 들어가는 것:
- 비즈니스 로직
- 데이터 가공
- 여러 저장소/외부 API 조합
- 비용 계산
- 통계 생성
- 예외 처리 정책

예:
```python
def get_data_by_date(date: str) -> EnergyDataResponse:
    record = repo.get_by_date(date)
    if not record:
        raise ValueError("No data found")

    return EnergyDataResponse(...)
```

##### service의 책임
- 앱의 핵심 동작 정의
- “어떻게 처리할지” 결정
- router와 DB 사이 중간 관리자 역할

즉 service는 **두뇌**에 가깝습니다.

---

#### ③ Repository / Database 계층
**기준:** DB나 외부 저장소와 직접 통신하는 코드인가?

여기에 들어가는 것:
- Firestore 읽기/쓰기
- SQL 쿼리
- 컬렉션 접근
- 저장소별 형식 처리

예:
```python
def get_by_date(date: str):
    doc = db.collection("energy_data").document(date).get()
    return doc.to_dict()
```

##### repository의 책임
- 저장소 접근
- CRUD 수행
- DB 세부 구현 숨기기

즉 service는  
“데이터 가져와줘”라고만 말하고,  
**어디서 어떻게 가져오는지는 repository가 담당**합니다.

---

#### ④ Models / Schemas 계층
**기준:** 데이터 구조를 정의하는 코드인가?

여기에 들어가는 것:
- 요청 모델
- 응답 모델
- 검증 규칙
- 타입 정의

예:
```python
class EnergyDataResponse(BaseModel):
    id: str
    date: str
    value: float
```

##### models의 책임
- 데이터 형식 표준화
- 검증
- 문서화

즉 model은 **데이터 계약서**입니다.

---

### 3. 이 프로젝트에 대입하면

지금 보고 있는 프로젝트는 대략 이렇게 나뉘죠.

---

#### `api/routes/data.py`
**왜 분리?**  
→ HTTP API 엔드포인트를 모아두기 위해

여긴:
- `/summary`
- `/{date}`
- `GET/POST/PUT/DELETE`
같은 API 경로를 담당합니다.

즉,
> “어떤 URL로 들어왔을 때 어떤 서비스 함수를 부를까?”

를 결정하는 곳이에요.

---

#### `services/data_service.py`
**왜 분리?**  
→ 에너지 데이터 처리 규칙을 모아두기 위해

여긴:
- 데이터 생성/조회/수정/삭제 로직
- 요약 통계 계산
- DB 결과를 응답 모델로 변환

즉,
> “이 요청을 실제로 어떻게 처리할까?”

를 담당합니다.

---

#### `db/firestore.py`
**왜 분리?**  
→ Firestore 접근 코드를 한곳에 몰아두기 위해

여긴:
- 인증
- 클라이언트 생성
- 컬렉션 접근
- mock 모드 지원

즉,
> “Firestore랑 어떻게 연결할까?”

를 담당합니다.

---

#### `models/data_models.py`
**왜 분리?**  
→ 입력/출력 데이터 형식을 한곳에 정의하기 위해

여긴:
- `EnergyDataCreate`
- `EnergyDataUpdate`
- `EnergyDataResponse`
- `SummaryResponse`

즉,
> “데이터는 어떤 모양이어야 할까?”

를 정합니다.

---

#### `services/ai_service.py`
**왜 분리?**  
→ AI 관련 로직은 일반 데이터 CRUD와 성격이 다르기 때문

여긴:
- 대화 처리
- tool calling
- 컨텍스트 주입
- AI 응답 생성

즉,
> “AI와 대화하는 로직”은 일반 데이터 서비스와 분리하는 게 자연스럽습니다.

---

### 4. 가장 중요한 분리 기준: 관심사의 분리(Separation of Concerns)

이게 핵심 개념입니다.

각 파일/계층이 **한 종류의 관심사만 갖게** 만드는 거예요.

예를 들어:

- router는 HTTP에만 관심
- service는 비즈니스 규칙에만 관심
- repository는 DB 접근에만 관심
- model은 데이터 구조에만 관심

이렇게 되면 코드가 훨씬 읽기 쉬워집니다.

---

### 5. “기능별 분리”와 “역할별 분리” 차이

둘 다 쓰이지만, 보통 함께 섞어서 씁니다.

---

#### 역할별 분리
예:
- routers
- services
- models
- db

장점:
- 계층이 명확
- 책임이 잘 보임

---

#### 기능별 분리
예:
- energy/
- ai/
- auth/

장점:
- 도메인 중심으로 보기 쉬움

---

실무에서는 보통 **둘을 같이** 씁니다.

예:
```python
app/
  routers/
    data.py
    chat.py
  services/
    data_service.py
    ai_service.py
  models/
    data_models.py
  db/
    firestore.py
```

즉:
- 큰 기준은 역할별
- 그 안에서 기능별 파일 분리

---

### 6. 왜 service 계층이 특히 중요한가?

많은 초보 프로젝트는 router와 service를 안 나눕니다.  
그런데 프로젝트가 커질수록 service가 진짜 중요해져요.

왜냐하면 비즈니스 로직은 여러 곳에서 재사용되기 때문입니다.

예:
- API 라우터에서 사용
- AI tool에서 사용
- 배치 작업에서 사용
- 테스트 코드에서 사용

만약 모든 로직이 router 안에 있으면,
HTTP 요청이 아닌 곳에서는 재사용하기 어려워져요.

즉 service를 두면:

> **핵심 로직을 HTTP와 분리**할 수 있습니다.

이게 엄청 큰 장점이에요.

---

### 7. DB 코드를 service에서 바로 쓰지 않고 또 분리하는 이유

예를 들어 service가 바로 Firestore 코드를 쓰면:

```python
def get_data_by_date(date: str):
    doc = firestore_client.collection(...).document(...).get()
```

이렇게 되면 문제:
- Firestore에 강하게 묶임
- DB 바꾸기 어려움
- 테스트 어려움
- service가 너무 많은 걸 앎

그래서 repository/db 계층으로 숨깁니다.

```python
def get_data_by_date(date: str):
    record = repo.get_by_date(date)
```

이제 service는  
“데이터를 가져온다”는 의미만 알고,  
Firestore 세부 구현은 몰라도 됩니다.

---

### 8. 분리했을 때 얻는 장점

1. 읽기 쉬움: 어디에 뭐가 있는지 예측 가능
2. 수정 쉬움:
    * DB 수정은 repository 중심  
    * 응답 형식 수정은 models 중심  
    * 비즈니스 규칙 수정은 service 중심
3. 테스트 쉬움
    * service만 따로 테스트 가능  
    * DB를 mock으로 대체 가능
4. 재사용 쉬움: router 말고 다른 곳에서도 service 사용 가능
5. 협업 쉬움: 팀원이 역할 분담하기 좋음

---

### 9. 한 문장씩으로 각 계층 정의

- **Router**: 요청을 받고 서비스에 전달한다.
- **Service**: 실제 처리 규칙을 수행한다.
- **Repository/DB**: 데이터를 저장/조회한다.
- **Model/Schema**: 데이터의 형식을 정의한다.

이렇게 기억하시면 됩니다.

---

### 10. 비유로 보면

레스토랑으로 비유하면:

- **Router** = 주문 받는 직원
- **Service** = 요리 방법을 결정하고 조리 흐름을 관리하는 주방
- **Repository/DB** = 냉장고/재료창고
- **Model** = 주문서/메뉴 규격

직원이 직접 재료창고 들어가서 요리까지 하면 혼란스럽겠죠.  
그래서 역할을 나누는 겁니다.

---

### 11. 실전 기준 하나 더: “이 코드가 바뀌는 이유가 무엇인가?”

이건 좋은 설계 기준입니다.

예를 들어:

- API 경로가 바뀌면 → router 수정
- 계산 규칙이 바뀌면 → service 수정
- Firestore 구조가 바뀌면 → db/repository 수정
- 응답 필드가 바뀌면 → models 수정

즉 **바뀌는 이유가 다른 코드끼리 분리**하는 거예요.

이 기준이 정말 중요합니다.

---

### 12. 결론

FastAPI 프로젝트를 라우터/서비스 등으로 분리한 기준은:

> **각 코드의 책임과 관심사가 다르기 때문**입니다.

구체적으로는:

- **router**: HTTP 요청/응답 담당
- **service**: 비즈니스 로직 담당
- **repository/db**: 데이터 저장소 접근 담당
- **models**: 데이터 구조/검증 담당

즉,  
**“무엇을 하느냐”에 따라 나눈 것**이지,  
단순히 파일 수를 늘리기 위해 나눈 게 아닙니다.

---

원하시면 다음엔 제가 이어서  
**이 프로젝트의 실제 함수 하나를 기준으로**  
`router → service → firestore → response_model`  
흐름을 화살표처럼 끝까지 연결해서 보여드릴게요.  
이렇게 보면 계층 분리가 더 직관적으로 이해됩니다.

<br>
</details>

---

# 3. Pydantic을 활용한 요청 데이터 검증

Pydantic을 활용한 요청 데이터 검증은, 클라이언트 입력이 올바른 구조와 타입을 갖는지 라우터 단계에서 자동으로 확인해서 잘못된 데이터가 서비스와 DB로 들어가는 것을 막기 위한 방식.

API를 통해 전달되는 데이터가 올바른 형식과 값을 가지는지 검증하기 위해 Pydantic 모델을 사용함. 예를 들어 날짜는 올바른 날짜 형식인지, 전력 사용량은 숫자이며 적절한 값인지 등을 API 요청 단계에서 확인함. 잘못된 데이터가 Service나 데이터베이스까지 전달되는 것을 방지함으로써 시스템의 안정성과 데이터 품질을 높일 수 있음. 또한 검증 규칙을 Pydantic 모델에 명확하게 정의하여 API의 입력 데이터 구조를 쉽게 이해하고 관리할 수 있도록 했음.

---

<details>
<summary>[상세 설명]</summary>
<br>

이건 FastAPI 프로젝트에서 **엄청 중요한 기본기**예요.

한 줄로 먼저 말하면:

> **Pydantic을 쓰는 이유는**  
> 클라이언트가 보낸 요청 데이터가 **형식에 맞는지 자동으로 검사**해서,  
> 잘못된 입력을 초기에 막고 안정적인 서비스를 만들기 위해서예요.

---

## 1. 왜 요청 데이터 검증이 필요한가요?

클라이언트가 보내는 데이터는 항상 믿을 수 없어요.

예를 들어 에너지 기록 생성 요청이 이렇게 와야 한다고 해봅시다:

```json
{
  "date": "2026-09-01",
  "value": 4.2
}
```

그런데 실제로는 이런 잘못된 요청이 올 수 있어요:

```json
{
  "date": "아무문자열",
  "value": "많이씀"
}
```

또는:

```json
{
  "value": 4.2
}
```

문제점:
- 날짜 형식이 이상함
- 숫자여야 할 값이 문자열임
- 필수 필드가 없음

이걸 검증하지 않으면:
- DB에 이상한 데이터 저장
- 분석 결과 깨짐
- 차트 오류
- AI 요약도 부정확해짐

즉:

> **입력 데이터가 깨지면, 뒤에 있는 모든 기능이 같이 흔들려요.**

---

## 2. Pydantic을 쓰는 이유

### 1) 자동 검증
필수 필드가 있는지, 타입이 맞는지 자동으로 검사합니다.

### 2) 코드가 깔끔해짐
직접 `if "date" not in body` 같은 코드를 매번 안 써도 돼요.

### 3) 에러 응답이 표준화됨
잘못된 요청이면 FastAPI가 자동으로 `422 Unprocessable Entity`와 함께 어떤 필드가 문제인지 알려줍니다.

### 4) 타입 변환 도움
문자열 숫자를 float로 변환하는 등 기본적인 파싱을 도와줍니다.

### 5) 문서화에 유리
Swagger/OpenAPI 문서에 요청 스키마가 자동으로 표시돼요.

---

## 3. 방식: Pydantic 모델을 먼저 정의해요

보통 `data_models.py` 같은 파일에 요청 구조를 정의합니다.

예시:

```python
from pydantic import BaseModel, Field
from datetime import date

class EnergyDataCreate(BaseModel):
    date: date
    value: float = Field(..., gt=0, description="에너지 사용량(kWh)")
```

#### 설명
- `BaseModel`: Pydantic 모델의 기본 클래스
- `date: date`: 날짜 형식이어야 함
- `value: float`: 숫자여야 함
- `Field(..., gt=0)`: 필수값이며 0보다 커야 함

즉 이 모델 자체가:

> “이 요청은 이런 모양이어야 한다”  
> 라는 계약서 역할을 해요.

---

## 4. FastAPI에서 어떻게 적용하나요?

라우터 함수 매개변수에 그 모델을 넣으면 됩니다.

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/data")
def create_data(payload: EnergyDataCreate):
    return {
        "message": "저장 성공",
        "data": payload
    }
```

여기서 핵심은:

- FastAPI가 요청 body(JSON)를 받음
- `EnergyDataCreate` 모델에 맞춰 검증함
- 통과하면 `payload`로 전달
- 실패하면 자동 에러 반환

---

## 5. 실제로 어떤 검증이 되나요?

예를 들어 요청:

```json
{
  "date": "2026-09-01",
  "value": 4.2
}
```

→ 정상 통과

---

요청:

```json
{
  "date": "잘못된날짜",
  "value": 4.2
}
```

→ 날짜 파싱 실패

---

요청:

```json
{
  "date": "2026-09-01",
  "value": -3
}
```

→ `gt=0` 조건 위반

---

요청:

```json
{
  "date": "2026-09-01"
}
```

→ `value` 누락

즉:

> **잘못된 입력을 라우터 진입 단계에서 바로 차단**하는 거예요.

---

## 6. 직접 검증하는 방식보다 왜 좋은가요?

직접 하면 이런 코드가 많아져요:

```python
body = request.json()

if "date" not in body:
    return {"error": "date 필요"}

if "value" not in body:
    return {"error": "value 필요"}

try:
    value = float(body["value"])
except:
    return {"error": "value는 숫자여야 함"}
```

이 방식은:
- 코드가 길어짐
- 중복 많음
- 실수하기 쉬움
- 유지보수 어려움

반면 Pydantic은:

```python
class EnergyDataCreate(BaseModel):
    date: date
    value: float = Field(..., gt=0)
```

이 한 모델로 규칙을 모아둘 수 있어요.

---

## 7. 서비스 구조에서의 장점

이 프로젝트 흐름으로 보면:

```text
클라이언트 요청
   ↓
FastAPI + Pydantic 검증
   ↓
검증 통과한 안전한 데이터
   ↓
data_service로 전달
   ↓
DB 저장 / 분석 수행
```

즉 서비스 계층은  
이미 어느 정도 **정상 데이터라고 믿고 처리**할 수 있어요.

이게 중요합니다.

왜냐하면 서비스 로직은 원래:
- 통계 계산
- 요약 생성
- 저장 처리

에 집중해야 하지, 매번 “이 값이 숫자인가?”부터 검사하면 역할이 섞이거든요.

즉:

> **Pydantic이 입력 검증을 맡아주고,  
> service는 비즈니스 로직에 집중하게 해줍니다.**

---

## 8. 조금 더 다양한 예시

### 예시 1: 채팅 요청 검증

```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    conversation_id: str | None = None
```

#### 의미
- `message`는 반드시 있어야 함
- 빈 문자열은 안 됨
- 너무 긴 입력도 제한 가능
- `conversation_id`는 선택값

---

### 예시 2: 수정 요청 모델

생성과 수정은 보통 다르게 설계하기도 해요.

```python
class EnergyDataUpdate(BaseModel):
    date: date | None = None
    value: float | None = Field(None, gt=0)
```

#### 의미
- 수정은 일부 필드만 보낼 수 있음
- 그래서 optional 처리

---

## 9. 추가 검증도 가능해요

단순 타입 말고 **사용자 정의 규칙**도 넣을 수 있어요.

예:

```python
from pydantic import BaseModel, field_validator
from datetime import date

class EnergyDataCreate(BaseModel):
    date: date
    value: float

    @field_validator("value")
    @classmethod
    def value_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("value는 0보다 커야 합니다.")
        return v
```

이건 더 복잡한 규칙이 필요할 때 유용해요.

---

## 10. Pydantic이 “검증 + 변환”도 해줍니다

이것도 꽤 중요해요.

예를 들어 요청 JSON의 날짜는 문자열로 오지만:

```json
{
  "date": "2026-09-01",
  "value": 4.2
}
```

모델에서 `date: date`라고 써두면,  
Pydantic이 이를 Python `date` 객체로 바꿔줄 수 있어요.

즉:

- 입력은 JSON
- 내부에서는 타입이 정리된 Python 객체

가 됩니다.

이 덕분에 이후 코드가 더 편해져요.

---

## 11. 에러 응답이 자동이라는 점도 큰 장점

예를 들어 잘못된 요청이 오면 FastAPI가 자동으로 이런 식의 응답을 줍니다:

```json
{
  "detail": [
    {
      "loc": ["body", "value"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```

이건 프론트엔드 입장에서도 좋아요. 왜냐하면 어느 필드가 잘못됐는지 알 수 있으니까요.

---

## 12. 이 프로젝트 문맥에서 정리하면

에너지관리 앱에서는 Pydantic을 통해 보통 이런 걸 검증할 수 있어요:

- 에너지 기록 생성 요청
- 에너지 기록 수정 요청
- AI 채팅 요청
- 대화 저장 요청
- 사용자 입력 필드 길이/범위

그리고 그 목적은:

1. 잘못된 데이터 저장 방지
2. 서비스 로직 단순화
3. API 문서 자동화
4. 프론트와의 계약 명확화

입니다.

---

## 13. 아주 간단한 전체 예시

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import date

app = FastAPI()

class EnergyDataCreate(BaseModel):
    date: date
    value: float = Field(..., gt=0)

@app.post("/energy")
def create_energy(data: EnergyDataCreate):
    return {
        "message": "정상 입력입니다.",
        "date": data.date,
        "value": data.value
    }
```

#### 흐름
- 클라이언트가 `/energy`로 JSON 전송
- FastAPI가 `EnergyDataCreate`로 검증
- 통과하면 함수 실행
- 실패하면 자동 에러 응답

---

## 14. 핵심 정리

### 왜 적용했나?
- 잘못된 요청을 초기에 막으려고
- DB와 서비스 로직을 보호하려고
- 코드 중복을 줄이고 유지보수를 쉽게 하려고
- API 입력 형식을 명확히 하려고

### 어떻게 적용하나?
1. `BaseModel`로 요청 스키마 정의
2. 타입과 제약조건 작성
3. 라우터 함수 매개변수에 모델 선언
4. FastAPI가 자동 검증/변환 수행

---

## 15. 한 문장 결론

> **Pydantic을 활용한 요청 데이터 검증은, 클라이언트 입력이 올바른 구조와 타입을 갖는지 라우터 단계에서 자동으로 확인해서 잘못된 데이터가 서비스와 DB로 들어가는 것을 막기 위한 방식**입니다.

<br>
</details>

---


# 4. Firestore 데이터 저장 및 CRUD 처리

전처리된 일별 전력 사용량 데이터를 Firestore에 저장하고, 애플리케이션에서 CRUD(Create, Read, Update, Delete) 방식으로 관리하도록 구성함. 새로운 데이터를 저장할 때는 Create, 데이터를 조회할 때는 Read, 기존 데이터를 수정할 때는 Update, 필요 없는 데이터를 삭제할 때는 Delete 작업을 수행함. Firestore 접근 로직은 별도의 계층에서 관리하여 API Router가 데이터베이스의 구체적인 구현 방식에 직접 의존하지 않도록 함. 이를 통해 데이터 저장소와 애플리케이션 로직을 분리하고 유지보수성을 높임.


| 작업 | Firestore 메서드 | 설명 |
|---|---|---|
| Create | `set()` / `add()` | 새 데이터 저장 |
| Read | `get()` / `stream()` / `where()` | 조회 |
| Update | `update()` | 일부 필드 수정 |
| Delete | `delete()` | 문서 삭제 |


```python
from firebase_admin import credentials, firestore, initialize_app

cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred)
db = firestore.client()

# Create
db.collection("energy_data").document("2026-09-01").set({
    "date": "2026-09-01",
    "value": 4.52,
    "memo": "Worked from home"
})

# Read
doc = db.collection("energy_data").document("2026-09-01").get()
if doc.exists:
    print(doc.to_dict())

# Update
db.collection("energy_data").document("2026-09-01").update({
    "value": 5.00
})

# Delete
db.collection("energy_data").document("2026-09-01").delete()
```

---

<details>
<summary>[상세 설명]</summary>
<br>

물론이죠 😊  
이제는 **Firestore를 실제 DB처럼 어떻게 저장하고 CRUD 하는지**를 이해하면 됩니다.

---

## 1. Firestore가 어떻게 생겼는지부터

Firestore는 기본적으로 **컬렉션(Collection) → 문서(Document)** 구조예요.

예를 들어 에너지 데이터를 저장한다면:

```text
energy_data (컬렉션)
 ├─ 2026-09-01 (문서 ID)
 │   ├─ date: "2026-09-01"
 │   ├─ value: 4.52
 │   └─ memo: "Worked from home"
 ├─ 2026-09-02
 │   ├─ date: "2026-09-02"
 │   ├─ value: 3.91
 │   └─ memo: "Office"
```

즉:

- **컬렉션** = 데이터 묶음 테이블 비슷한 것
- **문서** = 데이터 한 건
- **필드** = 문서 안의 값들

---

## 2. Python에서 Firestore 연결

보통 FastAPI 백엔드에서는 `firebase_admin`을 많이 씁니다.

예시:

```python
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
```

이제 `db`를 통해 Firestore에 접근할 수 있어요.

---

## 3. 데이터 저장(Create)

예를 들어 `"energy_data"` 컬렉션에 하루치 데이터를 저장한다고 해볼게요.

### 방법 1: 문서 ID를 직접 지정
```python
doc_ref = db.collection("energy_data").document("2026-09-01")
doc_ref.set({
    "date": "2026-09-01",
    "value": 4.52,
    "memo": "Worked from home"
})
```

#### 설명
- `"energy_data"` 컬렉션에
- 문서 ID를 `"2026-09-01"`로 정하고
- 데이터를 저장합니다.

이 방식은 날짜별로 1개씩 저장할 때 좋아요.

---

### 방법 2: 문서 ID 자동 생성
```python
doc_ref = db.collection("energy_data").add({
    "date": "2026-09-01",
    "value": 4.52,
    "memo": "Worked from home"
})
```

#### 설명
- Firestore가 랜덤한 문서 ID를 자동 생성해줍니다.
- 게시글, 채팅 메시지처럼 ID를 직접 정할 필요 없을 때 자주 씁니다.

---

## 4. 데이터 조회(Read)

### 4-1. 문서 1개 조회
```python
doc = db.collection("energy_data").document("2026-09-01").get()

if doc.exists:
    data = doc.to_dict()
    print(data)
```

#### 결과 예시
```python
{
    "date": "2026-09-01",
    "value": 4.52,
    "memo": "Worked from home"
}
```

#### 설명
- `.get()`으로 문서를 가져오고
- `.exists`로 존재 여부 확인
- `.to_dict()`로 Python 딕셔너리로 변환합니다.

---

### 4-2. 컬렉션 전체 조회
```python
docs = db.collection("energy_data").stream()

for doc in docs:
    print(doc.id, doc.to_dict())
```

#### 설명
- `stream()`은 컬렉션 안 문서들을 하나씩 순회할 수 있게 해줍니다.
- `doc.id`는 문서 ID
- `doc.to_dict()`는 실제 데이터

---

### 4-3. 조건 조회
예: value가 4 이상인 데이터만

```python
docs = db.collection("energy_data").where("value", ">=", 4).stream()

for doc in docs:
    print(doc.id, doc.to_dict())
```

---

## 5. 데이터 수정(Update)

문서 일부 필드만 수정할 수 있어요.

```python
db.collection("energy_data").document("2026-09-01").update({
    "value": 5.10,
    "memo": "Air conditioner used"
})
```

#### 설명
- 기존 문서에서 해당 필드만 바뀝니다.
- 없는 문서를 `update()`하면 에러가 날 수 있어요.

---

### `set()`과 `update()` 차이
이거 중요해요.

#### `set()`
```python
doc_ref.set({
    "date": "2026-09-01",
    "value": 4.52
})
```

- 문서 전체를 새로 저장
- 기존 내용이 덮어써질 수 있음

#### `update()`
```python
doc_ref.update({
    "value": 5.10
})
```

- 일부 필드만 수정
- 기존 다른 필드는 유지

---

## 6. 데이터 삭제(Delete)

### 문서 삭제
```python
db.collection("energy_data").document("2026-09-01").delete()
```

#### 설명
- 해당 문서가 삭제됩니다.

---

## 7. FastAPI 프로젝트에서 CRUD는 보통 어떻게 연결되나?

보통 구조는 이렇게 됩니다:

```text
router → service → firestore(db)
```

---

### 예시 1: Create

#### Router
```python
@router.post("/")
def create_data(payload: EnergyDataCreate):
    return data_service.create_data(payload)
```

#### Service
```python
def create_data(payload: EnergyDataCreate):
    doc_id = payload.date
    db.collection("energy_data").document(doc_id).set(payload.model_dump())

    return {
        "id": doc_id,
        **payload.model_dump()
    }
```

#### 흐름
1. 클라이언트가 POST 요청
2. router가 payload 받음
3. service가 Firestore에 저장
4. 저장 결과 반환

---

### 예시 2: Read

```python
def get_data_by_date(date: str):
    doc = db.collection("energy_data").document(date).get()

    if not doc.exists:
        return None

    return {
        "id": doc.id,
        **doc.to_dict()
    }
```

#### 설명
- 문서 하나 조회
- 없으면 `None`
- 있으면 dict 반환

---

### 예시 3: Update

```python
def update_data(date: str, payload: EnergyDataUpdate):
    doc_ref = db.collection("energy_data").document(date)

    update_fields = payload.model_dump(exclude_unset=True)
    doc_ref.update(update_fields)

    updated_doc = doc_ref.get()

    return {
        "id": updated_doc.id,
        **updated_doc.to_dict()
    }
```

#### 여기서 핵심
`exclude_unset=True`는  
**사용자가 보낸 값만 수정**하게 해줍니다.

예를 들어 사용자가 memo만 보내면 value는 그대로 두는 거예요.

---

### 예시 4: Delete

```python
def delete_data(date: str):
    doc_ref = db.collection("energy_data").document(date)
    doc_ref.delete()

    return {"message": f"{date} deleted"}
```

---

## 8. 프로젝트 관점에서 보면

당신이 보고 있는 프로젝트에서는 아마 이런 흐름일 가능성이 커요:

---

### `firestore.py`
여기서는 DB 연결을 관리합니다.

예:
```python
class FirestoreDB:
    def __init__(self):
        self.db = firestore.client()

    def get_collection(self, name: str):
        return self.db.collection(name)
```

즉:
- 인증
- 클라이언트 생성
- 컬렉션 접근

을 담당해요.

---

### `data_service.py`
여기서는 Firestore에서 가져온 raw 데이터를  
Pydantic 모델로 바꿔서 반환합니다.

예:
```python
def get_data_by_date(date: str) -> EnergyDataResponse:
    doc = firestore_db.get_collection("energy_data").document(date).get()

    if not doc.exists:
        raise ValueError("Data not found")

    data = doc.to_dict()

    return EnergyDataResponse(
        id=doc.id,
        date=data["date"],
        value=data["value"],
        memo=data.get("memo")
    )
```

즉 service는:
- DB 결과 해석
- 예외 처리
- 응답 모델 변환

을 담당합니다.

---

## 9. CRUD를 한눈에 정리

| 작업 | Firestore 메서드 | 설명 |
|---|---|---|
| Create | `set()` / `add()` | 새 데이터 저장 |
| Read | `get()` / `stream()` / `where()` | 조회 |
| Update | `update()` | 일부 필드 수정 |
| Delete | `delete()` | 문서 삭제 |

---

## 10. 실무에서 자주 쓰는 패턴

### 날짜를 문서 ID로 쓰는 경우
```python
db.collection("energy_data").document("2026-09-01").set({...})
```

장점:
- 날짜로 바로 조회 가능
- 중복 저장 방지 쉬움

단점:
- 하루 1건만 자연스럽게 저장 가능

---

### 자동 ID 쓰는 경우
```python
db.collection("energy_data").add({...})
```

장점:
- 여러 건 저장 쉬움
- 유연함

단점:
- 특정 날짜 조회 시 query가 필요할 수 있음

---

## 11. 주의할 점

### 1) `set()`은 덮어쓸 수 있음
기존 문서가 있으면 내용이 바뀔 수 있어요.

### 2) `update()`는 없는 문서에 쓰면 실패 가능
수정 전에 문서 존재 여부를 확인하는 습관이 좋습니다.

### 3) 조회 후 `to_dict()` 필요
Firestore 문서는 바로 dict가 아니라 snapshot이라서 변환해야 해요.

### 4) 문서 ID와 데이터 필드를 어떻게 설계할지 중요
예: 날짜를 ID로 쓸지, 자동 ID로 쓸지

---

## 12. 아주 간단한 전체 예시

```python
from firebase_admin import credentials, firestore, initialize_app

cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred)
db = firestore.client()

# Create
db.collection("energy_data").document("2026-09-01").set({
    "date": "2026-09-01",
    "value": 4.52,
    "memo": "Worked from home"
})

# Read
doc = db.collection("energy_data").document("2026-09-01").get()
if doc.exists:
    print(doc.to_dict())

# Update
db.collection("energy_data").document("2026-09-01").update({
    "value": 5.00
})

# Delete
db.collection("energy_data").document("2026-09-01").delete()
```

이 코드 하나에 CRUD가 다 들어 있습니다.

---

## 13. 핵심만 정말 짧게 말하면

Firestore CRUD는 이렇게 기억하면 됩니다:

- **저장(Create)**: `set()` / `add()`
- **조회(Read)**: `get()` / `stream()`
- **수정(Update)**: `update()`
- **삭제(Delete)**: `delete()`

그리고 FastAPI 프로젝트에서는 보통:

- router가 요청 받음
- service가 로직 처리
- firestore.py가 DB 연결 담당

으로 나눕니다.

---

원하시면 다음엔 제가 이어서  
**이 프로젝트 스타일로 `create/read/update/delete` 함수를 하나씩 직접 써서**  
`data_service.py` 형태로 예제 만들어드릴게요.  
그렇게 보면 바로 실전에 연결됩니다 👍

<br>
</details>

---


# 5. 데이터 요약을 시스템 프롬프트에 주입하는 방식 — context 주입

AI가 전력 사용량에 대한 질문에 답변할 수 있도록 Firestore의 전체 데이터를 그대로 전달하는 대신, 애플리케이션에서 먼저 주요 통계와 분석 결과를 요약함. 생성된 요약 정보를 AI의 시스템 프롬프트에 컨텍스트로 포함하여 모델이 실제 사용자 데이터를 기반으로 답변하도록 구성함. 이를 통해 불필요하게 많은 원본 데이터를 모델에 전달하지 않으면서도 평균 사용량, 최대·최소 사용량, 월별 패턴과 같은 주요 질문에 답변할 수 있음. 또한 요약 정보에 존재하지 않는 값을 AI가 임의로 추측하지 않도록 데이터 기반 응답 원칙을 함께 적용함.

```text
Firestore
   ↓
data_service가 데이터 조회/요약
   ↓
ai_service가 요약 문자열 생성
   ↓
system prompt에 삽입
   ↓
OpenAI API 호출
   ↓
AI가 요약을 참고해서 답변
```

---

<details>
<summary>[상세 설명]</summary>
<br>

> **컨텍스트 주입**은  
> AI가 원래 모르는 앱의 내부 데이터(예: 에너지 사용 요약)를  
> **시스템 프롬프트에 텍스트로 넣어서**,  
> 마치 “알고 있는 것처럼” 답하게 만드는 방식입니다.

---

## 1. 왜 필요한가요?

LLM(챗GPT 같은 모델)은 기본적으로:

- 지금 DB에 뭐가 있는지 모르고
- 우리 Firestore 데이터도 모르고
- 사용자의 최근 에너지 기록도 자동으로 알지 못합니다

즉 모델은 **앱 내부 실시간 데이터에 접근권한이 없어요.**

그래서 백엔드가 먼저 데이터를 읽고 정리한 뒤, 그 내용을 프롬프트에 넣어줘야 합니다.

---

## 2. 시스템 프롬프트에 주입한다는 뜻

예를 들어 시스템 프롬프트가 원래는 이런 역할이죠:

```text
너는 친절한 에너지 관리 도우미다.
```

여기에 데이터 요약을 붙입니다:

```text
너는 친절한 에너지 관리 도우미다.

현재 사용자 데이터 요약:
- 총 30일 데이터가 있음
- 평균 사용량: 4.2 kWh
- 최고 사용일: 2026-09-03 (6.1 kWh)
- 최저 사용일: 2026-09-10 (2.8 kWh)
- 최근 7일 평균: 4.8 kWh
- 전체 추세: 지난주보다 소폭 증가

이 정보를 바탕으로 답변하되, 데이터에 없는 내용은 추측하지 마라.
```

이렇게 하면 모델은 답변할 때 이 요약을 **배경지식처럼 참고**합니다.

---

## 3. 원리: “모델이 DB를 읽는 게 아니라, 텍스트를 읽는다”

이게 핵심입니다.

많이 헷갈리는 부분이:

> “AI가 Firestore를 직접 읽는 건가요?”

보통 **아니에요.**

실제 원리는 이렇습니다:

1. 백엔드가 Firestore에서 데이터 조회
2. 서비스 계층이 그 데이터를 요약
3. 그 요약을 문자열(text)로 만듦
4. 그 문자열을 `system` 메시지에 포함
5. LLM은 그 텍스트를 읽고 답변

즉 AI는 DB 객체를 이해하는 게 아니라, **백엔드가 만든 설명문**을 읽는 거예요.

---

## 4. 전체 흐름

이 프로젝트 식으로 보면 대략 이런 흐름입니다:

```text
Firestore
   ↓
data_service가 데이터 조회/요약
   ↓
ai_service가 요약 문자열 생성
   ↓
system prompt에 삽입
   ↓
OpenAI API 호출
   ↓
AI가 요약을 참고해서 답변
```

---

## 5. 예시 흐름으로 보기

사용자가 질문:

> “최근 전력 사용 패턴이 어때?”

그러면 백엔드가 먼저:

```python
summary = {
    "count": 30,
    "avg_usage": 4.2,
    "recent_7d_avg": 4.8,
    "trend": "increasing",
    "max_day": "2026-09-03",
    "max_value": 6.1
}
```

이걸 프롬프트용 텍스트로 바꿉니다:

```python
context_text = f"""
현재 사용자 에너지 데이터 요약:
- 기록 수: {summary['count']}일
- 평균 사용량: {summary['avg_usage']} kWh
- 최근 7일 평균: {summary['recent_7d_avg']} kWh
- 추세: {summary['trend']}
- 최고 사용일: {summary['max_day']} ({summary['max_value']} kWh)
"""
```

그리고 시스템 프롬프트에 넣어요:

```python
messages = [
    {
        "role": "system",
        "content": f"""
너는 에너지 관리 도우미다.
다음 사용자 데이터를 참고해서 답변해라.

{context_text}

데이터에 없는 사실은 추측하지 마라.
"""
    },
    {
        "role": "user",
        "content": "최근 전력 사용 패턴이 어때?"
    }
]
```

그러면 모델은 이 텍스트를 바탕으로 예를 들어 이렇게 답할 수 있어요:

> 최근 7일 평균 사용량이 전체 평균보다 높아 최근 사용량이 증가하는 경향이 있습니다. 특히 2026-09-03에 최고 사용량 6.1kWh가 기록되었습니다.

---

## 6. 왜 “요약”해서 넣나요?

아주 중요합니다.

Firestore의 모든 원본 데이터를 프롬프트에 다 넣을 수도 있지만, 보통은 **요약해서 넣는 게 더 좋습니다.**

이유:

### 1) 토큰 절약
LLM에 보내는 텍스트가 길수록 비용과 지연이 커집니다.

### 2) 핵심만 전달
모델은 정돈된 정보를 더 잘 활용합니다.

### 3) 노이즈 감소
불필요한 raw data가 많으면 답변 품질이 떨어질 수 있어요.

### 4) 개인정보/민감정보 제한
필요한 정보만 골라서 넣을 수 있습니다.

즉:

> **DB 전체를 넣는 게 아니라, 답변에 필요한 핵심만 압축해서 넣는 것**  
> 이 컨텍스트 주입의 실전 포인트예요.

---

## 7. 시스템 프롬프트를 쓰는 이유

프롬프트에는 보통 여러 역할이 있죠:

- `system`
- `user`
- `assistant`

여기서 데이터 요약을 보통 `system`에 넣는 이유는:

> **AI가 항상 우선적으로 참고해야 하는 배경 규칙/상황**이기 때문입니다.

예를 들어:

- 너는 어떤 역할인지
- 어떤 데이터가 현재 있는지
- 무엇을 기준으로 답해야 하는지
- 추측하면 안 되는지

이런 건 `system`에 두는 게 자연스럽습니다.

---

## 8. 컨텍스트 주입과 Function Calling 차이

이 부분도 자주 헷갈려요.

---

### 컨텍스트 주입
미리 데이터를 넣어줌

- 장점: 빠름, 간단함
- 단점: 이미 넣은 정보만 활용 가능

예:
- 평균 사용량
- 최근 추세
- 총 기록 수

---

### Function Calling
필요할 때 AI가 도구를 호출함

- 장점: 더 정확하고 동적
- 단점: 구현 복잡

예:
- “2026-09-03 데이터 자세히 보여줘”
- “최근 3개월 합계 계산해줘”

---

즉,

- **자주 필요한 공통 정보** → 컨텍스트 주입
- **정확한 실시간 조회/세부 분석** → function calling

이렇게 같이 쓰는 경우가 많아요.

---

## 9. 이 방식의 장점

### 1) AI가 앱 상황을 이해한 것처럼 답함
그냥 일반론만 말하는 게 아니라  
실제 사용자 데이터 기반 답변처럼 보이게 됩니다.

### 2) 구현이 단순함
DB 결과를 문자열로 넣기만 하면 되니까 비교적 쉽습니다.

### 3) 빠름
질문마다 도구 호출을 여러 번 안 해도 됩니다.

### 4) 오프라인/폴백에도 유리
최소한의 요약만 있어도 어느 정도 답변 가능

---

## 10. 한계도 있어요

### 1) 주입한 내용 이상은 모름
요약에 없는 세부사항은 답 못 할 수 있어요.

### 2) 오래된 컨텍스트일 수 있음
요약을 미리 만들었다면 최신 DB 상태와 다를 수 있습니다.

### 3) 너무 많이 넣으면 오히려 비효율
프롬프트가 길어지고 중요도가 흐려질 수 있어요.

### 4) 텍스트 기반이라 구조적 정확성 한계
숫자가 많고 복잡하면 함수 호출이 더 적합할 수 있어요.

---

## 11. 그래서 보통 어떻게 설계하나요?

실무적으로는 이런 식이 좋아요:

#### 시스템 프롬프트에 넣는 것
- 사용자 데이터 요약
- 최근 추세
- 평균값
- 최고/최저 값
- 답변 규칙

#### 도구 호출로 처리하는 것
- 특정 날짜 상세 조회
- 조건 검색
- 최신 데이터 다시 가져오기
- 복잡한 계산

즉:

> **요약은 배경지식**  
> **툴 호출은 정밀조회**

라고 생각하면 됩니다.

---

## 12. 아주 쉬운 비유

AI를 새로 온 상담원이라고 생각해보세요.

이 상담원은 회사 DB를 직접 볼 수 없어요.  
대신 직원이 메모를 써서 건넵니다:

```text
이 고객은 최근 전력 사용량이 증가 중이고,
지난주 평균은 4.8kWh이며,
최고 사용일은 9월 3일이다.
```

상담원은 그 메모를 읽고 고객에게 답합니다.

이 메모가 바로 **컨텍스트 주입**이에요.

즉:

- DB 직접 조회 = 아님
- 메모 전달 = 맞음

---

## 13. 코드 관점에서 핵심 형태

아주 단순화하면 이런 구조예요:

```python
def build_system_prompt(summary_text: str) -> str:
    return f"""
너는 친절한 에너지 관리 AI다.
다음 사용자 데이터 요약을 참고해서 답변해라.

{summary_text}

데이터에 없는 내용은 추측하지 마라.
"""
```

```python
summary_text = data_service.get_summary_text()
system_prompt = build_system_prompt(summary_text)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_message},
]
```

여기서 핵심은:

- `data_service`가 데이터를 요약하고
- `ai_service`가 그걸 시스템 프롬프트에 넣는다

는 점입니다.

---

## 14. 핵심 정리

### 컨텍스트 주입의 원리
- AI는 DB를 직접 아는 게 아니다
- 백엔드가 데이터를 먼저 요약한다
- 그 요약을 시스템 프롬프트에 텍스트로 넣는다
- 모델은 그 텍스트를 읽고 답변한다

### 왜 쓰나
- 사용자 맞춤 답변을 위해
- 빠르고 간단하게 앱 데이터를 반영하려고

### 장점
- 구현 쉬움
- 빠름
- 공통 정보 전달에 적합

### 한계
- 세부 조회에는 약함
- 너무 길면 비효율
- 최신성 관리 필요

---

## 15. 한 문장 결론

> **컨텍스트 주입은 “실제 DB 데이터”를 AI에게 직접 연결하는 것이 아니라,  
> 그 데이터를 요약한 텍스트를 시스템 프롬프트에 넣어 AI의 답변 배경지식으로 쓰는 방식**입니다.

---

원하시면 다음엔 이어서  
**`ai_service.py`의 `process_chat()` 안에서 컨텍스트가 언제 만들어지고 messages에 어떻게 들어가는지**  
코드 흐름처럼 단계별로 설명해드릴게요.

<br>
</details>

---

# 6. 배포 환경에서 CORS / 환경변수 / 키 관리가 필요한 이유

프론트와 백엔드가 안전하게 통신하고, 환경마다 다른 설정을 유연하게 적용하며, 비밀정보를 외부에 노출하지 않기 위해서.

프론트엔드와 백엔드가 서로 다른 도메인에서 실행될 수 있기 때문에 브라우저의 보안 정책에 따라 필요한 API 요청을 허용하도록 CORS를 설정해야 함. API Key나 Firebase 인증 정보와 같은 민감한 값은 소스 코드에 직접 작성하지 않고 환경변수를 통해 관리하여 외부에 노출되지 않도록 함. 특히 OpenAI API Key는 브라우저의 프론트엔드 코드에 포함하지 않고 백엔드에서만 사용하도록 구성해야 함. 이러한 설정은 로컬 개발 환경과 실제 배포 환경을 분리하고, 인증 정보의 노출 위험을 줄이는 데 중요함.

* CORS(Cross-Origin Resource Sharing) 설정: 보안상의 이유로 브라우저는 다른 도메인(Origin)에서 오는 API 요청을 기본적으로 차단. 예를 들어, 프론트엔드(http://localhost:3000)가 백엔드(http://localhost:8000)에 데이터를 요청하려면 백엔드에서 "이 도메인의 접근을 허용하겠다"고 명시해야 함. 이를 처리해 주는 설정임.
* 보안 때문입니다. 아무 사이트나 사용자의 브라우저를 통해 내 API에 마음대로 요청하면 위험하겠죠. 그래서 브라우저는 기본적으로: “이 프론트엔드가 저 백엔드에 요청해도 되는지?” 를 확인합니다. 이걸 제어하는 규칙이 **CORS**임.

---

<details>
<summary>[상세 설명]</summary>
<br>

배포 환경에서 **CORS / 환경변수 / 키 관리**가 중요한 이유는 한마디로:

> **앱이 “안전하게”, “환경에 맞게”, “비밀정보를 노출하지 않고” 동작하게 만들기 위해서**예요.

---

## 1. CORS가 왜 필요한가요?

### 먼저 상황부터
배포하면 보통 이렇게 나뉘어요:

- 프론트엔드: `https://my-app.vercel.app`
- 백엔드(FastAPI): `https://my-api.onrender.com`

이때 브라우저 입장에서는 **서로 다른 출처(origin)** 입니다.

출처는 보통 다음이 다르면 달라져요:
- 도메인
- 프로토콜 (`http`, `https`)
- 포트

예:
- `http://localhost:3000`
- `http://localhost:8000`

이 둘도 서로 다른 origin이에요.

---

### 브라우저는 왜 막나요?
보안 때문입니다.

아무 사이트나 사용자의 브라우저를 통해 내 API에 마음대로 요청하면 위험하겠죠.

그래서 브라우저는 기본적으로:

> “이 프론트엔드가 저 백엔드에 요청해도 되는지?”

를 확인합니다. 이걸 제어하는 규칙이 **CORS**예요.

---

### FastAPI에서 CORS가 없으면?
프론트엔드에서 API 호출할 때 이런 문제가 납니다:

- 브라우저 콘솔에 CORS 에러
- 백엔드는 살아 있어도 브라우저가 응답을 막음
- 프론트엔드에서 fetch/axios 요청 실패

즉:

> 서버 문제라기보다, **브라우저가 보안상 차단**하는 거예요.

---

### 그래서 배포 환경에서 왜 꼭 설정해야 하나요?
개발 때는 `localhost`만 쓰지만, 배포하면 주소가 바뀝니다.

예:
- 개발 프론트: `http://localhost:3000`
- 운영 프론트: `https://energy-app.vercel.app`

이제 백엔드는 이 출처들을 허용해야 해요.

예시:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://energy-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 의미
- 이 주소들에서 오는 요청만 허용
- 프론트가 백엔드와 통신 가능

---

### 주의
```python
allow_origins=["*"]
```
이렇게 전부 허용하면 편하지만,  
운영에서는 너무 넓게 열 수 있어요.

특히 인증/쿠키가 있으면 더 조심해야 합니다.

---

## 2. 환경변수가 왜 필요한가요?

환경변수는 **설정값을 코드 밖에서 주입하는 방법**이에요.

예를 들면 이런 값들:

- DB 이름
- Firestore 설정
- OpenAI API Key
- DEBUG 여부
- 프론트엔드 주소
- API base URL

---

### 왜 코드에 직접 쓰면 안 되나요?

예를 들어:

```python
OPENAI_API_KEY = "sk-xxxxx"
FRONTEND_URL = "http://localhost:3000"
```

이렇게 하드코딩하면 문제점이 많아요.

#### 문제 1) 환경이 바뀔 때마다 코드 수정
- 로컬 개발
- 테스트 서버
- 운영 서버

환경마다 값이 다른데, 코드까지 계속 바꿔야 해요.

#### 문제 2) 비밀정보 유출 위험
GitHub에 올라가면 API 키가 노출될 수 있어요.

#### 문제 3) 협업이 불편
사람마다 로컬 환경이 다를 수 있는데 코드를 계속 수정하면 꼬입니다.

---

### 환경변수의 핵심 장점

#### 1) 개발/배포 설정 분리
같은 코드라도 환경변수만 다르게 넣으면 됩니다.

예:
- 로컬: `DEBUG=true`
- 운영: `DEBUG=false`

#### 2) 민감정보를 코드 밖으로 분리
API 키를 소스코드에 안 넣어도 됩니다.

#### 3) 배포 플랫폼에 맞게 쉽게 설정
Render, Railway, GCP, Vercel 같은 곳에서  
환경변수를 UI로 등록할 수 있어요.

---

### 예시

```python
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
```

또는 Pydantic Settings를 쓸 수도 있어요.

---

### `.env` 파일은 뭔가요?
개발할 때 환경변수를 편하게 관리하려고 쓰는 파일입니다.

예:
```env
OPENAI_API_KEY=sk-xxxxx
FRONTEND_URL=http://localhost:3000
FIRESTORE_PROJECT_ID=my-project
```

하지만 중요한 점:

> `.env`는 **로컬 개발 편의용**이고,  
> 운영 배포에서는 보통 플랫폼의 환경변수 설정을 사용합니다.

그리고 `.env`는 꼭 `.gitignore`에 넣어야 해요.

---

## 3. 키 관리가 왜 필요한가요?

여기서 키는 보통 이런 것들이에요:

- OpenAI API Key
- Firebase 서비스 계정 키
- DB 접속 비밀번호
- JWT secret key

이건 전부 **비밀(secret)** 입니다.

---

### 왜 위험한가요?
키가 노출되면 남이 내 서비스 권한으로 행동할 수 있어요.

예를 들어:
- OpenAI 키 노출 → 남이 내 비용으로 API 사용
- Firebase 서비스 계정 키 노출 → DB 읽기/쓰기 가능
- JWT secret 노출 → 위조 토큰 위험

즉 키는 곧 **권한**이에요.

---

### 키 관리를 제대로 안 하면 생기는 일
1. 비용 폭탄
2. 데이터 유출
3. 데이터 변조/삭제
4. 서비스 악용
5. 보안 사고 대응 필요

---

## 4. “모든 키가 다 똑같이 비밀인가요?”

아니에요. 이 구분이 중요합니다.

---

### 1) 공개되어도 되는 설정
예:
- 프론트엔드에서 쓰는 Firebase 웹 설정 일부
  - apiKey
  - authDomain
  - projectId

이건 이름만 보면 비밀 같지만,  
Firebase 웹 클라이언트 설정은 **보통 공개 전제**인 경우가 많아요.

즉:
- 클라이언트에서 써야 하므로 노출될 수 있음
- 대신 보안은 Firebase Rules 등으로 막음

---

### 2) 절대 서버에만 있어야 하는 비밀
예:
- OpenAI API Key
- Firebase Admin SDK 서비스 계정 키
- DB 관리자 비밀번호
- JWT secret

이건 브라우저로 보내면 안 됩니다.

즉:

> **프론트엔드에 들어가는 값**과  
> **백엔드 서버에만 있어야 하는 값**을 구분해야 해요.

---

## 5. 왜 “배포 환경”에서 더 중요해지나요?

로컬에서는 혼자 테스트하니까 대충 넘어가기도 해요.  
하지만 배포하면:

- 실제 사용자 접근
- 공개 인터넷 노출
- 비용 발생 가능
- 여러 환경(dev/staging/prod) 존재
- 협업/운영 필요

즉 배포는 장난감 코드가 아니라 **운영 중인 서비스**가 되는 순간이에요.

그래서:
- CORS는 누가 접근 가능한지 제어하고
- 환경변수는 환경별 설정을 분리하고
- 키 관리는 비밀정보를 보호합니다

---

## 6. 이 프로젝트에 연결해서 보면

에너지 관리 앱 기준으로 보면:

---

### CORS
프론트엔드(`Vercel`)에서 FastAPI 백엔드(`Render`)로 요청하니까 필요

예:
- 에너지 데이터 조회
- AI 채팅 요청
- CRUD 요청

없으면 브라우저가 막아요.

---

### 환경변수
배포 환경마다 이런 값이 달라질 수 있어요:

- `OPENAI_API_KEY`
- `FIRESTORE_PROJECT_ID`
- `FRONTEND_URL`
- `ENV=development|production`
- `MOCK_MODE=true|false`

이걸 코드에 박아두면 관리가 힘들어요.

---

### 키 관리
특히 중요한 것:
- Firestore Admin 서비스 계정
- OpenAI API 키

이건 절대 프론트엔드 JS에 넣으면 안 돼요.  
반드시 **FastAPI 서버 쪽 환경변수/시크릿 저장소**에만 둬야 합니다.

---

## 7. 실전 예시

### 잘못된 예
```javascript
// 프론트엔드 JS에 비밀키 직접 작성
const OPENAI_API_KEY = "sk-xxxxx";
```

이건 브라우저 개발자도구에서 다 보입니다. 절대 안 돼요.

---

### 올바른 구조
#### 프론트엔드
```javascript
fetch("https://my-api.onrender.com/chat", {
  method: "POST",
  body: JSON.stringify({ message: "안녕" })
});
```

#### 백엔드
```python
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

즉:
- 프론트는 백엔드만 호출
- 백엔드가 비밀키로 외부 API 호출

---

## 8. CORS, 환경변수, 키 관리의 관계

이 셋은 따로 보이지만 실제로는 연결돼 있어요.

### CORS
“어떤 프론트엔드가 이 API를 호출할 수 있지?”

### 환경변수
“운영/개발 환경에 따라 어떤 설정값을 쓸까?”

### 키 관리
“비밀 권한 정보는 어디에 안전하게 둘까?”

즉 셋 다 **배포 안정성 + 보안**을 위한 장치예요.

---

## 9. 꼭 기억할 실무 포인트

### CORS
- 프론트 배포 주소를 allowlist에 넣기
- 로컬/운영 주소 구분하기

### 환경변수
- 설정값은 코드 밖으로 빼기
- `.env`는 로컬용
- 운영은 배포 플랫폼 시크릿 사용

### 키 관리
- 비밀키는 절대 프론트에 두지 않기
- GitHub에 올리지 않기
- 필요하면 키 회전(rotation) 하기
- 최소 권한 원칙 적용하기

---

## 10. 한 줄씩 요약

- **CORS**: 브라우저가 다른 출처의 API 요청을 허용할지 제어하는 보안 규칙
- **환경변수**: 코드 수정 없이 환경별 설정을 바꾸기 위한 방법
- **키 관리**: API 키/비밀번호 같은 비밀정보를 안전하게 보호하는 운영 습관

---

## 11. 한 문장 결론

> 배포 환경에서 CORS/환경변수/키 관리가 필요한 이유는,  
> **프론트와 백엔드가 안전하게 통신하고, 환경마다 다른 설정을 유연하게 적용하며, 비밀정보를 외부에 노출하지 않기 위해서**입니다.

---

원하시면 다음엔 이어서  
**이 프로젝트 기준으로 `.env`, FastAPI CORS 설정, OpenAI/Firestore 키를 어디에 둬야 하는지**를  
실제 예시 파일 형태로 정리해드릴게요 👍

<br>
</details>

---

##  What happens when a user adds a new daily record?

Everything updates automatically in real time without refreshing the page.
Here is the exact lifecycle when you add, edit, or delete a record:

    graph TD
        A["User submits '+ Add Day' / Edit / Delete"] --> B["API Call (POST / PUT / DELETE /api/data)"]
        B --> C["Backend persists changes to Firestore"]
        C --> D["Frontend triggers: Promise.all([loadDailyData(), loadSummary()])"]
        D --> E["loadDailyData()"]
        D --> F["loadSummary()"]
        E --> G["Daily Energy Data Table re-renders with new row on top"]
        E --> H["Electricity Consumption Chart re-plots new data point"]
        F --> I["Top 4 KPI Cards (Avg, Total, Peak, Lowest) recalculate"]
        F --> J["Energy Insights Panel recalculates (weekly pattern, trend, cost)"]

#### Specifically:

1. Daily Energy Data Table:
    * Updates immediately with the new record inserted at the top (sorted by date descending).
2. Electricity Consumption Chart (Visualization):
    * renderChart(records) is called automatically inside loadDailyData(). The new data point is integrated into the time series curve.
3. Top 4 KPI Cards:
    * renderSummary(summary) is called with fresh data from GET /api/data/summary.
    * Average / Day: Recalculates dynamically across all days.
    * Total Usage: Adds the new day's consumption.
    * Peak Day & Lowest Day: Evaluates whether the new value is a new maximum or minimum and updates the values and dates accordingly.
4. Energy Insights Panel:
    * renderInsights(summary) recalculates Weekday vs. Weekend consumption, Day-of-Week averages, recent 7-day and 30-day stats, and estimated total costs.



---

<details>
<summary>[상세 설명]</summary>
<br>



<br>
</details>

---
