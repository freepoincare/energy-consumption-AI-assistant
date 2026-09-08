# app/routers/data.py

이제 드디어 백엔드(서버)의 핵심부인 **FastAPI 라우터** 코드로 들어왔군요! 

`app/routers/data.py` 파일은 프론트엔드(`api.js`)에서 보낸 요청을 가장 먼저 맞이하는 **'접수 창구(Router)'** 역할을 합니다. 이 코드는 전력 데이터와 관련된 모든 길(Path)을 정의하고 있습니다.

핵심 내용을 4가지 파트로 나누어 설명해 드릴게요.

---

### 1. 라우터 설정 (Router Setup)
```python
router = APIRouter(prefix="/api/data", tags=["Energy Data"])
```
*   **`prefix="/api/data"`**: 이 라우터 안의 모든 주소 앞에 `/api/data`를 자동으로 붙여줍니다. (예: `/summary` -> `/api/data/summary`)
*   **`tags`**: 나중에 `/docs`(Swagger UI) 문서에서 이 기능들을 "Energy Data"라는 그룹으로 예쁘게 묶어줍니다.

### 2. AI를 위한 요약 정보 (`GET /summary`)
```python
@router.get("/summary", ...)
async def get_energy_summary():
    try:
        return EnergyDataService.get_summary()
    except Exception as e:
        raise HTTPException(...)
```
*   **역할**: 전체 데이터의 평균, 최대/최소값, 추세 등을 계산해서 가져옵니다.
*   **중요성**: 이 데이터는 AI 챗봇이 사용자의 전력 소비 패턴을 이해하기 위해 사용하는 **'학습 요약본'**이 됩니다.

### 3. 데이터 목록 조회 및 생성 (`GET`, `POST`)
*   **`GET ""` (목록 조회)**: 저장된 모든 일별 전력 데이터를 리스트 형태로 반환합니다.
*   **`POST ""` (데이터 추가)**: 새로운 날짜의 전력 사용량을 저장합니다.
    *   **방어적 프로그래밍**: 이미 해당 날짜의 데이터가 있다면 `409 CONFLICT` 에러를 내보내 중복 저장을 막습니다.

### 4. 특정 데이터 관리 (`GET`, `PUT`, `DELETE` with `{record_id}`)
여기서 `{record_id}`는 보통 **'2026-03-01'** 같은 날짜 문자열이 됩니다.
*   **`GET /{record_id}`**: 특정 날짜의 상세 정보를 가져옵니다.
*   **`PUT /{record_id}`**: 특정 날짜의 사용량이나 메모를 수정합니다.
*   **`DELETE /{record_id}`**: 특정 날짜의 데이터를 삭제합니다.

---

### 💡 이 코드의 주요 특징 (학습 포인트)

1.  **관심사 분리 (Service Layer 패턴)**:
    라우터는 "어떤 주소로 요청이 왔나?"만 확인하고, 실제 복잡한 계산이나 데이터베이스 작업은 `EnergyDataService`라는 별도의 클래스에 맡깁니다. (라우터는 접수만 하고, 실제 요리는 주방장이 하는 것과 같습니다.)

2.  **Pydantic 모델을 통한 검증**:
    `payload: EnergyDataCreate` 처럼 타입을 지정해두면, FastAPI가 들어오는 데이터가 올바른 형식인지 자동으로 검사해줍니다. (예: 숫자가 들어와야 할 곳에 문자가 오면 입구에서 컷!)

3.  **친절한 에러 메시지 (`HTTPException`)**:
    데이터가 없으면 `404 Not Found`, 중복되면 `409 Conflict` 등 표준 HTTP 상태 코드를 사용하여 프론트엔드(`api.js`)가 상황을 정확히 파악할 수 있게 돕습니다.

---

### 🌟 요약하자면
이 파일은 **"사용자가 전력 데이터를 보거나, 넣거나, 고치거나, 지우고 싶을 때 통과해야 하는 문"**들을 정의한 것입니다. 

프론트엔드의 `api.js`가 이 문들을 두드리면, 이 라우터가 `EnergyDataService`를 호출해 결과를 가져다주는 흐름이죠. 백엔드 구조가 아주 정석적으로 잘 짜여 있습니다! 

다음은 이 라우터가 호출하는 **`data_service.py`**나 실제 데이터 모델인 **`data_models.py`**가 궁금하신가요? 😊

---

## @router.get()

파이썬에서 함수 위에 `@`로 시작하는 코드를 **데코레이터(Decorator)**라고 부릅니다. FastAPI에서 `@router.get()`을 사용하는 이유는 크게 3가지로 요약할 수 있습니다.

### 1. "접수 창구"를 지정하는 역할 (Routing)
비유하자면, 서버는 아주 큰 **백화점**이고 함수(`get_energy_summary`)는 그 안에서 일하는 **직원**입니다. 손님이 백화점에 들어왔을 때, 어떤 직원을 찾아가야 할지 알려주는 **'안내 표지판'**이 바로 `@router.get()`입니다.

*   **`@router`**: "이 표지판은 우리 층(라우터) 소속이야."
*   **`.get`**: "손님이 데이터를 **가져오려고(GET)** 할 때만 안내해줘."
*   **`("/summary")`**: "손님이 **'/summary'**라는 문 앞에 서면 이 직원을 연결해줘."

이게 없다면, 파이썬은 이 함수가 '그냥 함수'인지, '웹 요청을 처리하는 함수'인지 알 방법이 없습니다.

### 2. HTTP 메서드 결정 (GET, POST, PUT, DELETE)
똑같은 주소라도 **어떤 행동**을 하느냐에 따라 다른 함수를 실행해야 합니다.
*   `@router.get("/data")`: 데이터를 **보여줄 때** 실행
*   `@router.post("/data")`: 데이터를 **새로 저장할 때** 실행

데코레이터를 통해 이 함수가 어떤 **HTTP 동작**에 반응할지 명확히 정의합니다.

### 3. 자동화 서비스 (FastAPI의 마법)
`@router.get()` 안에 여러 설정을 적어두면 FastAPI가 복잡한 일을 대신 해줍니다.
*   **데이터 검증**: `response_model=SummaryResponse`라고 써두면, 함수가 내뱉는 결과가 형식에 맞는지 자동으로 검사합니다.
*   **문서 자동 생성**: 우리가 쓴 `summary`, `description` 내용을 읽어서 **Swagger UI**(`.../docs`)라는 멋진 API 설명서를 자동으로 만들어줍니다.
*   **상태 코드 관리**: 성공했을 때 `200 OK`를 보낼지, `201 Created`를 보낼지 미리 정해둘 수 있습니다.

---

### 코드로 다시 보기

```python
@router.get(
    "/summary",                             # 1. 주소 (Path)
    response_model=SummaryResponse,         # 2. 응답 형식 검사
    status_code=status.HTTP_200_OK,         # 3. 성공 시 보낼 상태 코드
    summary="Get Energy Consumption Summary" # 4. 문서에 표시될 제목
)
async def get_energy_summary():             # 실제 일하는 직원(함수)
    return EnergyDataService.get_summary()
```

### 💡 요약하자면
`@router.get()`은 **"이 함수는 웹 브라우저가 `/api/data/summary`라는 주소로 GET 요청을 보냈을 때 실행될 함수야!"**라고 서버에게 공식적으로 등록하는 절차입니다.

이게 없으면 프론트엔드(`api.js`)에서 아무리 호출해도 서버는 "그런 주소는 모르겠는데요?"라고 대답하게 됩니다. 😊

---

### status_code=status.HTTP_200_OK

`status_code=status.HTTP_200_OK`는 개발자가 임의로(자유롭게) 정할 수 있지만, 아무 값이나 마구잡이로 정해서는 안 되며 '전 세계적인 웹 표준 규약'에 맞춰서 선택해야 합니다.

이 값은 클라이언트(앱, 웹 브라우저 등)가 이 API를 호출했을 때, 요청이 성공하면 서버가 "성공적으로 잘 처리되었어!"라고 알려주는 HTTP 상태 코드(Status Code)입니다.

#### 1. 왜 내 마음대로 숫자를 정하면 안 되나요?

HTTP 상태 코드는 전 세계 개발자들이 모여 만든 약속(Protocol)입니다.
만약 성공했는데 내 마음대로 200 대신 800이나 999 같은 숫자를 보내거나, 실패했는데도 200(성공)을 보내버리면 이 API를 사용하는 다른 개발자(또는 프론트엔드 앱)가 코드를 작성할 때 대혼란에 빠지게 됩니다.

#### 2. 그럼 어떤 기준으로 정해야 하나요? (가장 많이 쓰는 패턴)

현재 작성하신 API는 `@router.post("")`로 무언가 요청을 보내서 처리를 완료하는 기능을 하고 있습니다. 이때 보통 사용하는 코드는 딱 2가지입니다.

* `status.HTTP_200_OK` (200): 요청이 성공적으로 처리되었고, 그 결과 데이터(ChatResponse)를 본문(Body)에 담아서 돌려줄 때 사용합니다. (현재 작성하신 코드에 가장 적절합니다.)
* `status.HTTP_201_CREATED` (201): 요청을 통해 서버나 데이터베이스에 새로운 리소스(예: 새로운 채팅방, 새로운 유저 등)가 실제로 생성되었을 때 명확하게 구분하기 위해 사용합니다.

#### 3. HTTP 상태 코드 대표 그룹 (참고용)

숫자의 앞자리에 따라 대략적인 의미가 정해져 있습니다. 이 규칙 안에서 내 API의 목적에 맞는 숫자를 선택하시면 됩니다.

| 상태 코드 범위 | 의미 | 대표적인 예시 |
|---|---|---|
| 2xx (성공) | 요청을 성공적으로 받았고 처리함 | 200 OK (일반적인 성공), 201 Created (생성 완료) |
| 3xx (리다이렉션) | 요청을 완료하기 위해 추가 작업이 필요함 | 301 Moved Permanently (주소 이동) |
| 4xx (클라이언트 오류) | 요청 보낸 사람(클라이언트)의 잘못 | 400 Bad Request (잘못된 데이터 요청), 404 Not Found (없는 페이지) |
| 5xx (서버 오류) | 서버 내부 프로그램이나 시스템의 잘못 | 500 Internal Server Error (서버 터짐 / 코드 에러) |

---

# FastAPI에서 @router.get, @app.get이 왜 나뉘는지?

이건 **FastAPI 구조를 이해하는 핵심**이에요.

## 한 줄로 먼저
- `@app.get()` : **앱 전체에 직접 라우트를 붙이는 방식**
- `@router.get()` : **라우트를 모듈별로 묶어서 관리하는 방식**

즉,  
**작은 프로젝트는 `app.get`도 가능**하지만,  
**조금만 커지면 `router.get`이 훨씬 좋습니다.**

---

## 1. `@app.get()` 이란?

`app`은 FastAPI 애플리케이션 전체입니다.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

뜻:
- `GET /health` 요청이 오면
- `health_check()`가 처리한다

이건 가장 기본적인 방식이에요.

---

## 2. 그런데 왜 `@router.get()`이 필요할까?

프로젝트가 커지면 라우트가 많아져요.

예를 들면:
- `/health`
- `/api/data`
- `/api/chat`
- `/api/users`
- `/api/admin`
- `/api/reports`

이걸 전부 `app.py`에 쓰면 파일이 너무 커집니다.

그래서 기능별로 나누려고 `APIRouter`를 써요.

---

## 3. `@router.get()` 기본 형태

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}
```

여기서는 아직 앱에 직접 붙은 게 아니라,  
**라우트 묶음(router)을 만든 상태**예요.

그 다음 `app`에 연결해야 합니다.

```python
from fastapi import FastAPI
from myrouter import router

app = FastAPI()
app.include_router(router)
```

이제야 실제 앱에 등록돼요.

---

## 4. 왜 굳이 이렇게 나눌까?

### 이유 1) 파일 분리가 쉬움
예를 들어:

- `routers/data.py`
- `routers/chat.py`
- `routers/user.py`

처럼 기능별로 나눌 수 있어요.

#### data.py
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/data")
def get_data():
    return {"message": "data"}
```

#### chat.py
```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/chat")
def chat():
    return {"message": "chat"}
```

#### main.py
```python
from fastapi import FastAPI
from routers.data import router as data_router
from routers.chat import router as chat_router

app = FastAPI()

app.include_router(data_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
```

이렇게 하면:
- `/api/data`
- `/api/chat`

으로 동작해요.

---

### 이유 2) 관심사 분리가 됨
이건 아키텍처에서 아주 중요해요.

예를 들어:
- 채팅 관련 라우트는 `chat.py`
- 데이터 관련 라우트는 `data.py`

이렇게 두면 **어디에 무엇이 있는지 찾기 쉬워요.**

즉,
- 프론트에서 `/api/chat` 문제 생김 → `chat.py` 보면 됨
- `/api/data` 문제 생김 → `data.py` 보면 됨

---

### 이유 3) 재사용이 쉬움
`router`는 조립식처럼 붙였다 뗄 수 있어요.

예를 들어 개발 중에는:
- admin router 포함
운영 중에는:
- admin router 제외

이런 식으로 관리하기 쉬워집니다.

---

### 이유 4) prefix와 tags를 공통 적용 가능
이게 실무에서 아주 편해요.

```python
app.include_router(data_router, prefix="/api/data", tags=["data"])
```

그러면 `data_router` 안의 라우트들은 자동으로 `/api/data` 아래에 붙어요.

예:

```python
@router.get("/")
def read_data():
    return {"message": "all data"}

@router.get("/{item_id}")
def read_item(item_id: str):
    return {"item_id": item_id}
```

최종 URL은:
- `GET /api/data/`
- `GET /api/data/{item_id}`

이렇게 됩니다.

즉, 매번 긴 주소를 반복해서 안 써도 돼요.

---

## 5. `@app.get()`만 쓰면 안 되나요?

써도 됩니다. 하지만 **작을 때만** 괜찮아요.

예를 들어 테스트용 앱:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "hello"}

@app.get("/health")
def health():
    return {"status": "ok"}
```

이 정도는 괜찮아요.

그런데 기능이 많아지면:

```python
@app.get("/users")
@app.post("/users")
@app.get("/users/{id}")
@app.put("/users/{id}")
@app.delete("/users/{id}")
@app.get("/chat")
@app.post("/chat")
@app.get("/data")
@app.post("/data")
...
```

이렇게 한 파일이 너무 복잡해져요.

그래서 **확장 가능한 구조**를 위해 `router`를 씁니다.

---

## 6. 비유로 이해하기

### `app`
- 건물 전체 관리자

### `router`
- 부서별 담당자

예:
- 데이터 부서 router
- 채팅 부서 router
- 사용자 부서 router

그리고 `app.include_router(...)`는  
“이 부서를 건물 운영에 등록하자”라는 뜻이에요.

---

## 7. 실무에서 보통 이렇게 씁니다

### main.py
```python
from fastapi import FastAPI
from routers.data import router as data_router
from routers.chat import router as chat_router

app = FastAPI()

app.include_router(data_router, prefix="/api/data", tags=["data"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
```

### routers/data.py
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_all_data():
    return {"message": "data list"}
```

### routers/chat.py
```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def send_chat():
    return {"message": "chat response"}
```

최종 엔드포인트:
- `GET /api/data/`
- `POST /api/chat/`

이 구조가 바로 **라우터 기반 구조**예요.

---

## 8. 정리

### `@app.get()`
- FastAPI 앱에 직접 라우트 등록
- 간단한 프로젝트에 적합

### `@router.get()`
- 라우트를 기능별로 묶음
- 큰 프로젝트에 적합
- 유지보수, 확장, 파일 분리에 유리

### 둘의 관계
- `router.get()`으로 먼저 묶고
- `app.include_router()`로 최종 앱에 연결

---

## 9. 정말 핵심만 다시
**`app`은 전체 앱**,  
**`router`는 기능별 라우트 묶음**입니다.

그래서 FastAPI는:
- 작은 앱도 만들 수 있고
- 큰 앱도 깔끔하게 구조화할 수 있게

둘을 나눠 둔 거예요.

---

원하시면 다음에는 이어서  
**`app.include_router(router, prefix="/api", tags=["data"])`가 정확히 어떻게 동작하는지**  
한 줄씩 분석해드릴게요.