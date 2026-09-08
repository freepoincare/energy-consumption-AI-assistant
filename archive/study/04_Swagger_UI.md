# Swagger UI

어떤 데이터가 오고 가는지 쉽게 파악하고 협업.

Swagger UI는 개발자가 작성한 API(REST API)의 구조를 웹 브라우저에서 시각적으로 보여주고, 직접 테스트할 수 있도록 도와주는 오픈소스 인터페이스 툴입니다.
개발자가 API 스펙(OpenAPI Specification)을 JSON이나 YAML 형식으로 등록하면, 이를 기반으로 깔끔한 웹 페이지를 자동으로 생성해 줍니다. 특히 FastAPI를 사용할 경우, 개발자가 별도의 설정을 하지 않아도 이 Swagger UI 페이지가 완전히 자동으로 만들어집니다.

## 핵심 기능 3가지

* API 시각화 (Visual Doc): 서버에 어떤 URL(Endpoint)이 있는지, GET/POST/PUT/DELETE 중 어떤 메서드를 쓰는지 한눈에 보여줍니다.
* input/output 구조 표시 (Schema): API를 호출할 때 어떤 데이터(JSON, 쿼리 파라미터 등)를 보내야 하고, 성공이나 실패 시 어떤 데이터가 돌아오는지 상세한 규격을 보여줍니다.
* 즉시 테스트 (Try it out): Postman 같은 외부 프로그램 없이, 브라우저 화면에서 직접 데이터를 입력해 서버로 요청을 보내고 응답 결과를 확인할 수 있습니다.

## Swagger UI가 필요한 이유

Swagger UI가 필요한 가장 핵심적인 이유는 백엔드 개발자가 API 문서를 따로 작성하고 관리하는 번거로움을 없애고, 프론트엔드 개발자와의 협업 효율을 극대화하기 위함.
코드를 변경할 때마다 문서를 수동으로 업데이트할 필요가 없어 비즈니스 로직에만 집중.
구체적인 이유는 다음과 같습니다.

### 1. 살아있는 문서화 (Living Documentation)

* 실시간 동기화: 코드를 수정하고 서버를 재시작하면 문서가 자동으로 업데이트됩니다.
* 최신 상태 유지: "코드와 API 문서가 다르다"는 개발 인터페이스의 고질적인 문제가 원천 차단.

### 2. 브라우저에서 즉시 테스트 (Interactive Sandbox)

* Postman 대체: 별도의 API 테스트 툴(Postman, Insomnia 등)을 켤 필요가 없습니다.
* 원클릭 요청: 웹 브라우저에서 Try it out 버튼을 눌러 파라미터를 입력하고, 실제 서버에 요청을 보내 응답(Response) 데이터 구조를 즉시 확인.

### 3. 완벽한 협업 도구 (Frontend-Backend Alignment)

* 명확한 규격 공유: 프론트엔드 개발자, 앱 개발자, QA 엔지니어에게 Swagger URL 한 장만 공유하면 모든 소통이 해결됩니다.
* 에러 구조 파악: 성공(200 OK) 응답뿐만 아니라 에러(400, 422, 500 등) 발생 시 어떤 형태의 JSON이 반환되는지 미리 정의된 스키마를 통해 쉽게 알 수 있습니다.

### 4. 보안 및 인증 테스트 지원 (Authorize Feature)

* JWT/OAuth2 지원: 상단의 Authorize 버튼을 통해 토큰(Token)이나 API Key를 한 번만 등록해 두면, 로그인이 필요한 인증 기반 API들도 브라우저에서 손쉽게 테스트할 수 있습니다.

---

FastAPI와 Swagger UI를 결합하여 사용하실 계획인가요?

* Swagger UI에서 JWT 토큰 인증(Bearer Token)을 설정하는 코드가 필요하신가요?
* API 문서에 상세한 설명(Description)이나 예시 데이터(Example JSON)를 추가하는 방법이 궁금하신가요?

---

현재 개발 중이거나 구상 중인 프로젝트가 있으신가요? 다음 중 원하시는 단계를 선택해 주시면 바로 지원해 드릴 수 있습니다.

* FastAPI에서 Swagger UI를 열어보고 기본적인 사용법을 익히고 싶으시다면 관련 가이드를 안내해 드립니다.
* 문서 화면에 내 API에 대한 한글 설명이나 예시 데이터(Example)를 깔끔하게 추가하는 방법을 코드로 보여드릴 수 있습니다.
* 보안이 필요한 API를 위해 Swagger UI 상단에 자물쇠 버튼(로그인/토큰 인증 기능)을 붙이는 방법을 알려드릴 수 있습니다.

--------------------------------------------------------------------------------------

Swagger UI는 “백엔드 API를 눈으로 보고 바로 시험해보는 웹 페이지”라고 이해하면 됩니다.

---

## 1. Swagger UI가 뭔가요?

FastAPI를 실행하면 보통 자동으로 생기는 문서 페이지입니다.

예:
- `/docs` → Swagger UI
- `/openapi.json` → API 명세 원본 데이터

즉, 백엔드가 “내가 어떤 API를 제공하는지” 자동으로 정리해서 보여주는 도구예요.

---

## 2. 왜 필요한가요?

### 핵심 이유 1) API를 한눈에 볼 수 있음
프론트엔드나 개발자가 백엔드 코드를 안 열어도:

- 어떤 주소가 있는지
- GET인지 POST인지
- 어떤 데이터를 보내야 하는지
- 어떤 응답이 오는지

바로 확인할 수 있어요.

---

### 핵심 이유 2) 직접 테스트 가능
Swagger UI에서는 버튼만 눌러서 API를 호출할 수 있어요.

예를 들어:
- `GET /health` 눌러보기
- `POST /api/chat`에 JSON 넣고 실행해보기

즉, Postman 없이도 간단히 실험할 수 있어요.

---

### 핵심 이유 3) 프론트-백 협업이 쉬워짐
프론트는 Swagger UI를 보고

- 요청 형식
- 응답 형식
- 필수 필드

를 확인한 뒤 API 연결을 할 수 있어요.

그래서
**“백엔드가 뭐 받는지 모르겠어요”**
같은 문제가 줄어듭니다.

---

### 핵심 이유 4) Pydantic 모델과 연결돼서 정확함

FastAPI는 `Pydantic` 모델을 쓰면 Swagger UI에 자동 반영해 줍니다.

예를 들어 요청 모델이 있으면:
- 어떤 필드가 필요한지
- 문자열인지 숫자인지
- 예시가 뭔지

문서에 자동으로 나와요.

이게 아주 큰 장점입니다.

---

## 3. 이 프로젝트에서는 왜 특히 중요할까요?

지금 배우는 프로젝트는 단순한 한두 개 API가 아니라:

- 데이터 조회/저장 API
- AI 채팅 API
- 대화 관리 API
- 상태 확인 API

처럼 여러 기능이 있죠.

이럴 때 Swagger UI가 있으면  
**API 전체 구조를 지도처럼 볼 수 있어요.**

즉:
- 어떤 라우트가 있는지
- 각 라우트가 어떤 모델을 쓰는지
- 응답이 어떤 구조인지

빠르게 파악할 수 있습니다.

---

## 4. 이 프로젝트에서는 어떻게 쓰나요?

보통 FastAPI 앱을 실행한 뒤 브라우저에서:

```text
http://localhost:8000/docs
```

또는 배포 후:

```text
https://백엔드주소.onrender.com/docs
```

로 들어가면 Swagger UI를 볼 수 있어요.

---

## 5. 이 프로젝트에서 Swagger UI가 보여주는 것

예를 들면 이런 정보가 나옵니다:

- `GET /health`
- `GET /api/data/...`
- `POST /api/chat`
- 기타 conversation 관련 API

각 API를 클릭하면:

1. 설명
2. 파라미터
3. Request Body
4. Response 예시
5. Execute 버튼

이런 게 나옵니다.

---

## 6. 특히 이 프로젝트에서 중요한 포인트

### 1) `router` 구조를 문서로 확인 가능
우리가 배운 `@router.get`, `@router.post` 들이  
최종적으로 Swagger UI에 나타나요.

즉,
코드에서 나뉘어 있던 여러 router가  
문서에서는 하나의 API 목록처럼 보입니다.

---

### 2) `response_model`이 왜 중요한지 보임
우리가 전에 본 `response_model`은  
“응답이 어떤 형태여야 하는지”를 정해 주는 역할이었죠.

Swagger UI에서는 이 `response_model` 덕분에:

- 응답 JSON 구조
- 각 필드 타입
- 중첩 구조

가 자동 문서화됩니다.

즉,  
**response_model = Swagger 문서 품질을 높여주는 핵심 요소**예요.

---

### 3) `Pydantic` 모델이 입력 양식을 만들어 줌
예를 들어 채팅 API가 어떤 요청 모델을 받는다면:

```python
class ChatRequest(BaseModel):
    message: str
    user_id: str
```

Swagger UI는 이걸 보고 자동으로:

```json
{
  "message": "string",
  "user_id": "string"
}
```

같은 입력 예시를 보여줘요.

그래서 프론트가 요청 형식을 헷갈리지 않습니다.

---

## 7. 실제 사용 흐름 예시

예를 들어 AI 채팅 API가 있다고 해볼게요.

### 코드
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    return {"reply": f"안녕하세요, {req.user_id}님"}
```

### Swagger UI에서 보이는 것
- `POST /chat`
- Request body:
```json
{
  "message": "string",
  "user_id": "string"
}
```

- Response:
```json
{
  "reply": "string"
}
```

즉, 코드가 문서로 자동 변환되는 거예요.

---

## 8. 프론트엔드 입장에서 왜 유용한가요?

프론트는 Vercel에서 돌아가고,  
백엔드는 Render에서 돌아가죠.

이때 프론트 개발자는 Swagger UI를 보고:

- 어떤 URL로 요청해야 하는지
- POST body를 어떻게 보내야 하는지
- 응답에서 어떤 필드를 꺼내야 하는지

바로 확인할 수 있어요.

즉, Swagger UI는  
**프론트와 백엔드를 연결해 주는 설명서** 역할을 합니다.

---

## 9. 디버깅할 때도 유용함
예를 들어 프론트에서 채팅이 안 된다면:

1. 먼저 Swagger UI에서 `POST /api/chat` 직접 호출
2. 여기서 되면 → 프론트 요청 형식 문제일 가능성 큼
3. 여기서도 안 되면 → 백엔드 로직/서버 문제

이렇게 문제를 빨리 분리할 수 있어요.

이건 실무에서도 정말 많이 씁니다.

---

## 10. 이 프로젝트에서 Swagger UI의 의미를 한 문장으로
**FastAPI 백엔드가 제공하는 모든 API를 자동으로 정리하고, 직접 테스트까지 할 수 있게 해 주는 도구**입니다.

---

## 11. 정리

### Swagger UI가 필요한 이유
- API 목록을 한눈에 볼 수 있음
- 직접 호출해서 테스트 가능
- 프론트-백 협업이 쉬워짐
- Pydantic/response_model 문서화가 자동화됨
- 디버깅이 쉬워짐

### 이 프로젝트에서는
- `/docs`에서 API 전체 구조 확인
- `data.py`, `chat`, conversation 관련 라우트 테스트
- 요청/응답 모델 확인
- 프론트 연결 전에 백엔드 단독 검증

---

## 12. 아주 짧게 비유하면
- **FastAPI 코드** = 기계 내부 설계도
- **Swagger UI** = 사용 설명서 + 시험 조작 패널

---

**이 프로젝트의 `/docs`에 실제로 어떤 항목들이 보일지 추정해서 하나씩 읽는 법**도 설명해드릴게요.

-----------------------------------------------------------------------------------------------

# Swagger UI 테스트 방법? 여기서 테스트 하면 바로 배포 환경에 적용이 되나요?

결론부터 말하면:

## 핵심 답
- **Swagger UI 테스트는 실제 API 요청을 보내는 것**입니다.
- 그래서 **어느 서버의 `/docs`에서 테스트하느냐에 따라 영향 범위가 달라집니다.**
- **배포 서버의 `/docs`에서 POST/PUT/DELETE를 실행하면, 실제 배포 환경 데이터에 반영될 수 있습니다.**

---

## 1. Swagger UI 테스트는 어떻게 하나요?

보통 FastAPI 실행 후:

- 로컬: `http://localhost:8000/docs`
- 배포: `https://내백엔드주소.onrender.com/docs`

로 들어갑니다.

그러면 API 목록이 보이고, 테스트는 보통 이렇게 합니다.

---

### 테스트 순서

#### 1) 테스트할 API 선택
예:
- `GET /health`
- `POST /api/chat`
- `GET /api/data/...`

클릭하면 상세 정보가 펼쳐집니다.

---

#### 2) `Try it out` 버튼 클릭
Swagger UI는 처음엔 읽기 전용처럼 보이는데,  
`Try it out`을 누르면 입력할 수 있게 바뀝니다.

---

#### 3) 필요한 값 입력
예를 들어 `POST` 요청이면 JSON body를 넣습니다.

예:
```json
{
  "message": "안녕하세요",
  "user_id": "test-user"
}
```

`GET /items/{id}` 같은 경우는 path parameter를 입력합니다.

예:
```text
id = 123
```

---

#### 4) `Execute` 클릭
그러면 Swagger UI가 **실제 HTTP 요청**을 서버로 보냅니다.

그리고 아래에 결과가 나옵니다:

- Request URL
- Curl 명령어
- Response status code
- Response body

---

## 예시

```python
@router.get("/health")
def health_check():
    return {"status": "ok"}
```

Swagger UI에서:
1. `GET /health` 클릭
2. `Try it out`
3. `Execute`

결과:
```json
{
  "status": "ok"
}
```

---

## 2. Swagger UI 테스트는 “가짜 테스트”인가요?

아니요.  
**진짜 요청**입니다.

즉 Swagger UI는 단순 문서가 아니라, 그 자리에서 실제 API를 호출하는 도구예요.

그래서:

- `GET` → 실제 조회
- `POST` → 실제 생성
- `PUT/PATCH` → 실제 수정
- `DELETE` → 실제 삭제

가 일어납니다.

---

## 3. 그럼 여기서 테스트하면 바로 배포 환경에 적용되나요?

### 답: “어디서 열었는지”에 따라 다릅니다.

---

### 경우 1) 로컬 `localhost:8000/docs` 에서 테스트
이건 **내 컴퓨터에서 실행 중인 백엔드**로 요청이 갑니다.

즉:
- 로컬 서버만 테스트
- 로컬 DB / 로컬 mock / 로컬 환경변수 사용
- 보통 배포 환경에는 직접 영향 없음

예:
```text
http://localhost:8000/docs
```

여기서 테스트하면 **내 로컬 개발 서버**에 요청하는 거예요.

---

### 경우 2) 배포 서버 `/docs` 에서 테스트
예:
```text
https://my-backend.onrender.com/docs
```

여기서 `Execute`를 누르면  
**실제 배포된 Render 백엔드**로 요청이 갑니다.

즉:
- 배포 서버 로직 실행
- 배포 DB 연결
- 실제 저장/수정/삭제 가능

그래서 **운영 데이터가 바뀔 수 있습니다.**

---

## 4. 특히 어떤 요청을 조심해야 하나요?

### 안전한 편
- `GET`
- `HEAD`
- 상태 확인 API (`/health`)

이건 보통 읽기 중심이라 상대적으로 안전합니다.

---

### 조심해야 함
- `POST`
- `PUT`
- `PATCH`
- `DELETE`

이건 데이터를 바꾸는 요청이라 배포 환경 `/docs`에서 실행하면 실제 데이터에 영향 줄 수 있어요.

예:
- 대화 저장됨
- 사용자 데이터 수정됨
- 문서 삭제됨

---

## 5. 이 프로젝트에서는 어떻게 봐야 하나요?

지금 프로젝트는 데이터 API, 채팅 API, 대화 관리 API가 있죠.

그래서 Swagger UI 테스트 시:

### 예를 들어
- `GET /health`  
  → 서버 살아있는지 확인, 안전

- `POST /api/chat`  
  → AI 응답 생성, 경우에 따라 대화 저장될 수 있음

- `POST /api/data` / `PUT` / `DELETE`  
  → 실제 데이터 변경 가능성 있음

즉, **읽기 API인지 쓰기 API인지 먼저 구분하고 테스트해야 합니다.**

---

## 6. “배포 환경 반영 여부”를 판단하는 체크 포인트

테스트 전에 이 3개를 꼭 보세요.

### 1) 지금 접속한 주소가 localhost인가?
- `localhost` → 로컬
- `onrender.com` 등 실제 도메인 → 배포

---

### 2) 백엔드가 어떤 DB를 쓰고 있는가?
예를 들어:
- Mock 모드
- 로컬 파일 저장
- Firestore 개발용 컬렉션
- Firestore 운영용 컬렉션

에 따라 영향이 달라집니다.

즉, 배포 서버라도 **운영 DB가 아니라 테스트 DB**를 쓰도록 설계되어 있으면 상대적으로 안전할 수 있어요.

---

### 3) 해당 API가 저장/수정/삭제를 하는가?
코드에서 확인해야 합니다.

예:
```python
@router.post("/chat")
def chat(...):
    ...
```

이게 단순 응답만 반환하는지,  
아니면 내부에서 `save_conversation()` 같은 걸 호출하는지 봐야 해요.

---

## 7. Swagger UI에서 테스트할 때 좋은 습관

### 1) 먼저 `GET /health`부터 확인
서버가 살아 있는지 먼저 확인합니다.

---

### 2) 조회 API 먼저 테스트
`GET` 위주로 구조를 파악하세요.

---

### 3) 쓰기 API는 테스트용 데이터로
예:
```json
{
  "user_id": "test-user",
  "message": "swagger test"
}
```

운영 사용자 데이터를 건드리지 않도록  
**테스트용 ID, 테스트용 문구**를 쓰는 게 좋아요.

---

### 4) DELETE는 특히 조심
삭제는 되돌리기 어렵습니다.

---

### 5) 가능하면 개발/스테이징 환경에서 먼저
실무에서는 보통:
- dev
- staging
- production

환경을 나눠서 테스트합니다.

운영 `/docs`는 읽기 확인 정도만 하고, 쓰기 테스트는 개발용 서버에서 하는 게 안전해요.

---

## 8. Swagger UI가 보내는 요청은 어디서 확인하나요?

`Execute` 후 아래에 이런 정보가 나옵니다:

- **Request URL**
- **Server response**
- **Response body**
- **Curl**

여기서 특히 **Request URL**을 보면  
내가 지금 로컬에 쏜 건지, 배포 서버에 쏜 건지 바로 확인할 수 있어요.

---

## 9. 실수 방지용 한 줄 규칙

### 이 규칙 기억하세요:
> **Swagger UI는 문서가 아니라 실제 API 호출기다.**

그래서 `/docs`에 있다고 해서 안전한 게 아닙니다.  
버튼을 누르면 진짜 요청이 나갑니다.

---

## 10. 추천 테스트 순서

이 프로젝트에서라면 보통 이렇게 합니다:

1. `GET /health`  
   → 서버 정상 확인

2. 데이터 조회 GET API  
   → 응답 구조 확인

3. 채팅 POST API  
   → 테스트용 메시지로 실행

4. 저장/수정/삭제 API  
   → 개발 환경에서만 신중히 테스트

---

## 11. 짧은 정리

### Swagger UI 테스트 방법
- `/docs` 접속
- API 선택
- `Try it out`
- 값 입력
- `Execute`

### 배포 환경에 바로 적용되나요?
- **로컬 `/docs`** → 로컬 환경에만 영향
- **배포 `/docs`** → 배포 환경에 실제 영향 가능

### 주의할 점
- `GET`은 비교적 안전
- `POST/PUT/PATCH/DELETE`는 실제 데이터 변경 가능

---

이걸 이해하면 Swagger UI를 훨씬 안전하게 쓸 수 있습니다.

원하시면 다음에는  
**이 프로젝트의 `/docs`에서 각 API를 보고 “이건 안전 / 이건 조심” 분류하는 방법**도 같이 해드릴게요.

---

# my-app.onrender.com/openapi.json vs. my-app.onrender.com/docs vs. my-app.onrender.com/redoc

Swagger UI(/docs), ReDoc(/redoc), openapi.json은 모두 FastAPI나 NestJS 같은 웹 프레임워크가 API를 문서화하고 제공하는 서로 다른 방식입니다.
가장 핵심적인 차이는 openapi.json이 API의 '데이터 원본(설명서)'이고, /docs와 /redoc은 그 데이터를 사람이 보기 좋게 시각화해 주는 '뷰어(UI)'라는 점입니다.

------------------------------
## 1. openapi.json (API 데이터 원본)

* 역할: 내 서버에 어떤 API가 있고, 어떤 파라미터를 받으며, 어떤 응답을 주는지 기계가 읽을 수 있는 형식(JSON)으로 작성된 명세서 원본입니다.
* 특징: 웹 브라우저로 접속하면 디자인 없이 가독성 낮은 복잡한 텍스트(JSON)만 보입니다.
* 용도: /docs나 /redoc 같은 UI 툴이 이 파일을 읽어서 화면을 그려냅니다. 또는 외부 프론트엔드 개발자가 이 JSON을 가져가서 자동으로 클라이언트 코드를 생성(Code Generation)할 때도 씁니다.

## 2. /docs (Swagger UI - 대화형 문서)

* 역할: openapi.json 기반으로 만들어진 Swagger UI 개발자 페이지입니다.
* 특징: 테스트(Try it out) 기능이 있어서 브라우저에서 즉시 API에 데이터를 넣고 요청을 날려볼 수 있습니다. 개발 단계에서 백엔드 개발자가 직접 테스트하거나 프론트엔드 개발자가 API 동작을 확인하기 가장 좋습니다.
* 화면 스타일: API들이 아래로 길게 나열되는 1단 구조입니다.

## 3. /redoc (ReDoc - 읽기 전용 문서)

* 역할: openapi.json 기반으로 만들어진 ReDoc UI 문서 페이지입니다.
* 특징: Swagger UI와 달리 화면에서 직접 API를 테스트하는 기능은 없습니다. 대신 훨씬 깔끔하고 정돈된 디자이너 인터페이스를 제공합니다.
* 화면 스타일: 왼쪽(메뉴 트리), 가운데(상세 설명), 오른쪽(코드 예시 및 응답 양식) 구조의 3단 레이아웃으로 되어 있어 대규모 API 문서를 읽고 분석하기에 가독성이 압도적으로 좋습니다.

------------------------------

## 📊 한눈에 보는 비교 표

| 구분 | openapi.json | /docs (Swagger UI) | /redoc (ReDoc) |
|---|---|---|---|
| 형태 | 순수 JSON 데이터 (기계용) | 웹 인터페이스 (인간용) | 웹 인터페이스 (인간용) |
| API 직접 테스트 | 불가능 | 가능 (Try it out) | 불가능 (읽기 전용) |
| 주요 목적 | API 명세 저장 및 코드 생성 | 개발 중 빠른 테스트 및 디버깅 | 외부 공개용 문서 및 깔끔한 가조성 |
| 화면 레이아웃 | 텍스트 나열 | 1단 세로 스크롤 방식 | 3단 분할 방식 (메뉴/설명/코드) |

보통 개발을 하고 테스트할 때는 주로 /docs를 켜놓고 작업하고, 이 API를 사용할 다른 팀원이나 외부 사용자에게 가독성 좋은 설명서를 제공할 때는 /redoc 주소를 공유하는 편입니다.
