# FastAPI

FastAPI: 빠르고 현대적인 파이썬 웹 API 프레임워크; API를 build하기 위함

Read: https://wikidocs.net/226651


<img src="https://static.wikidocs.net/images/page/226651/image_202604262256.png">


FastAPI는 Python을 사용한 웹 API 개발에 초점을 맞춘 빠르고 현대적인 웹 프레임워크입니다. Python의 타입 힌트(Type Hints)와 비동기 프로그래밍(ASGI)을 기반으로 설계되어 개발 속도와 실행 성능 모두에서 압도적인 퍼포먼스를 보여줍니다.

2026년 기준, 파이썬 백엔드 생태계의 사실상 표준(De facto standard)으로 자리 잡았으며, 특히 AI/LLM 서비스의 백엔드 API를 구축할 때 가장 널리 사용되는 프레임워크입니다.

## 최신 2026년 기준 주요 업데이트 및 특징

1. Pydantic v2 엔진 탑재로 극한의 성능 확보

    * 내부적으로 데이터 검증을 담당하는 Pydantic이 Rust 코어 기반의 v2로 업그레이드되면서, 기존 대비 JSON 파싱 및 데이터 유효성 검사 속도가 5배에서 최대 50배까지 빨라졌습니다. Node.js나 Go와 비견되는 고성능 I/O를 자랑합니다.

2. 공식 `fastapi` CLI 명령어 지원

    * 과거처럼 `uvicorn main:app --reload`를 직접 타이핑할 필요가 없어졌습니다. 이제 공식 내장된 `fastapi dev` (개발용 핫 리로드) 또는 `fastapi run` (운영 배포용) 명령어 하나로 완벽하게 서버를 구동할 수 있습니다.
    * `fastapi dev main.py`를 사용하려면 `pip install fastapi[standard]` 필요.

3. `Annotated`를 활용한 깔끔한 의존성 주입

    * 최신 FastAPI는 경로 매개변수나 의존성(Dependency)을 선언할 때 파이썬 표준인 `typing.Annotated` 사용을 강력히 권장합니다. 이를 통해 코드가 훨씬 깔끔해지고 정적 타입 분석기(Mypy, Pyright)와의 호환성이 완벽해졌습니다.

4. 자동 API 문서 생성 (Swagger UI)

    * 코드를 짜기만 하면 `/docs` 경로에 완벽하게 상호 작용 가능한 Swagger UI 문서가 자동으로 생성됩니다.

## 설치 방법

개발에 필요한 모든 도구(CLI, Uvicorn 서버 등)를 한 번에 설치합니다. (최신 패키지 매니저인 `uv` 사용을 권장합니다.)

```bash
# pip를 사용할 경우
pip install "fastapi[standard]"

# uv를 사용할 경우
uv add "fastapi[standard]"
```

`fastapi dev` 명령어를 사용하려면 `fastapi[standard]` 패키지를 설치해야 함.
기존에 `pip install fastapi`로 기본 패키지만 설치되어 있었다면 CLI 기능이 포함되어 있지 않으므로 실행되지 않습니다.

* `pip install fastapi` (기본 설치): 웹 프레임워크 핵심 기능만 설치됩니다. `fastapi` CLI 명령어나 Uvicorn 같은 서버 엔진이 포함되어 있지 않습니다.
* `pip install "fastapi[standard]"` (선택 옵션 포함 설치): `fastapi` CLI tool(`fastapi dev`, `fastapi run`), 서버 엔진(`uvicorn`), 데이터 검증 속도 향상을 위한 패키지(`pydantic-settings` 등)가 한 번에 함께 설치됩니다.

## 최신 예제 코드 (Annotated 및 Pydantic v2 반영)

```python
from typing import Annotated
from fastapi import FastAPI, Query, Body
from pydantic import BaseModel, Field

app = FastAPI()

# Pydantic v2 모델 정의
class Item(BaseModel):
    name: str = Field(..., description="아이템의 이름")
    description: str | None = None
    price: float = Field(..., gt=0, description="가격은 0보다 커야 합니다.")

# 루트 엔드포인트
@app.get("/")
async def read_root():
    return {"message": "Welcome to Modern FastAPI!"}

# Annotated를 사용한 최신 의존성 및 파라미터 선언 방식
@app.post("/items/{item_id}")
async def create_item(
    item_id: Annotated[int, Query(title="아이템 ID", ge=1)],
    item: Annotated[Item, Body(title="아이템 정보")]
):
    return {"item_id": item_id, "item_data": item}
```

실행 방법: 터미널에서 아래 명령어를 입력하면 즉시 서버가 실행되며 코드를 수정할 때마다 자동으로 재시작됩니다.

```bash
fastapi dev main.py
```

## 사용 사례

* AI 및 머신러닝 모델 서빙: TensorFlow, Pytorch, LangChain 기반의 AI 모델을 외부 서비스에서 호출할 수 있도록 빠르고 가볍게 API로 감쌀 때 최고의 선택입니다.
* 마이크로서비스 아키텍처(MSA): 가볍고 빠르며 자동화된 문서를 제공하여 여러 마이크로서비스 간의 통신용 API를 구축하는 데 적합합니다.

## 결론

FastAPI는 파이썬이 가진 '생산성'이라는 장점을 극대화하면서도 '성능'이라는 단점을 완벽하게 보완한 프레임워크입니다. 특히 Pydantic v2와 결합된 최신 버전은 더 이상 성능 타협이 필요 없는 수준에 도달했으며, 앞으로 파이썬으로 백엔드를 시작한다면 망설임 없이 선택해야 할 1순위 기술입니다.

---

# FastAPI

* high-performance web framework; one of the fatest pythyon frameworks

[FastAPI](https://fastapi.tiangolo.com/) is a modern, high-performance web framework for building APIs with Python based on standard Python type hints. It is widely recognized as one of the fastest Python frameworks available, delivering speeds comparable to NodeJS and Go. [1] 
Created by Sebastián Ramírez and first released in 2018, FastAPI is specifically designed to maximize developer productivity, minimize bugs, and effortlessly handle production-ready workloads. [1, 2] 

## Key Features & Benefits

* Automatic Interactive Documentation: The moment you create an endpoint, FastAPI automatically builds interactive API documentation using [Swagger UI](https://swagger.io/tools/swagger-ui/) and ReDoc. You can test your endpoints directly from your browser by simply navigating to /docs. [3, 4] 
* Data Validation and Serialization: By utilizing Python type hints alongside Pydantic, FastAPI automatically validates incoming request data. If a user sends the wrong data type (e.g., text instead of an integer), FastAPI rejects it with a clear error message before it touches your application logic. [2, 4] 
* Native Asynchronous Support: Built on top of [Starlette](https://www.starlette.io/), FastAPI uses the modern ASGI (Asynchronous Server Gateway Interface) standard. This allows it to handle thousands of concurrent connections and real-time features like WebSockets and Server-Sent Events natively and efficiently. [5, 6, 7] 
* Fewer Bugs & Great Editor Support: Because it relies heavily on Python type hints, modern code editors (like VS Code or PyCharm) provide excellent auto-completion, linting, and type-checking out of the box, reducing human error by roughly 40%. [1, 3] 
* Built-in Dependency Injection: It includes a robust and hierarchical dependency injection system, making it incredibly easy to manage database connections, authentication, and security logic uniformly across your routes. [7] 

## Architecture: How It Fits Together
FastAPI doesn't reinvent the wheel; it coordinates a powerful stack of underlying tools:

* Uvicorn: The lightning-fast ASGI server that runs your application and handles raw network requests.
* Starlette: The underlying toolkit that manages routing, cookies, sessions, and asynchronous operations.
* Pydantic: The data-parsing library that enforces data schemas and handles serialization.

## FastAPI vs. Other Python Frameworks

| Feature | FastAPI | Flask | Django |
|---|---|---|---|
| Type | Microframework (Asynchronous) | Microframework (Synchronous) | Full-stack "Batteries-Included" |
| Performance | Very High (Built for concurrency) | Moderate (Processes one request at a time per thread) | Moderate (Heavier architectural footprint) |
| Data Validation | Automatic (via Pydantic) | Manual (requires third-party packages) | Built-in (via Django Forms/ORM) |
| API Docs | Auto-generated (Swagger / ReDoc) | Manual | Manual (requires Django REST Framework) |
| Best Used For | Microservices, REST APIs, and AI/Machine Learning backends | Small apps, simple backends, quick prototypes | Complex, database-driven monolithic web applications |

## Example Application

Writing a basic backend API requires very few lines of code:

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}
```

---

FastAPI는 파이썬(Python) 표준 타입 힌트를 바탕으로 고성능 API를 빌드하기 위한 현대적인 웹 프레임워크입니다. NodeJS나 Go 언어에 비견될 정도로 매우 빠른 속도를 자랑하며, 개발 생산성을 극대화하고 버그를 최소화하도록 설계되었습니다.

## 🌟 주요 특징과 장점

* 자동 대화형 문서 생성: API 엔드포인트를 만드는 즉시, Swagger UI와 ReDoc을 활용한 대화형 API 문서가 자동으로 생성됩니다. 브라우저에서 /docs 경로로 접속하면 작성한 API를 즉시 테스트할 수 있습니다.
* 데이터 검증 및 직렬화: 파이썬 타입 힌트와 Pydantic 라이브러리를 사용하여 들어오는 요청 데이터를 자동으로 검증합니다. 사용자가 잘못된 데이터 타입(예: 숫자가 필요한 곳에 문자열)을 보내면 자동으로 명확한 에러를 반환합니다.
* 비동기(Async) 네이티브 지원: ASGI(Asynchronous Server Gateway Interface) 표준 기반의 Starlette을 내장하고 있어, 수많은 동시 연결과 웹소켓(WebSockets), 실시간 데이터 스트리밍을 효율적으로 처리합니다.
* 에디터 자동완성 및 버그 감소: 코드 전체에 타입 힌트를 사용하므로 VS Code, PyCharm 같은 에디터에서 강력한 자동완성, 타입 검사, 린팅을 지원하여 개발 중 실수를 줄여줍니다.
* 의존성 주입(Dependency Injection): 데이터베이스 연결, 사용자 인증, 보안 로직 등을 효율적이고 일관되게 관리할 수 있는 강력한 의존성 주입 시스템을 내장하고 있습니다.

## 📊 파이썬 대표 프레임워크 비교

| 기능 | FastAPI | Flask | Django |
|---|---|---|---|
| 종류 | 비동기 마이크로 프레임워크 | 동기 마이크로 프레임워크 | 풀스택 "Batteries-Included" |
| 성능 | 매우 높음 (동시성 처리에 최적화) | 보통 (기본적으로 스레드당 1요청) | 보통 (아키텍처가 무거운 편) |
| 데이터 검증 | 자동 지원 (Pydantic 활용) | 수동 (외부 패키지 필요) | 내장 (Django Forms/ORM 활용) |
| API 문서 | 자동 생성 (Swagger / ReDoc) | 수동 | 수동 (DRF 등 외부 패키지 필요) |
| 주요 용도 | 마이크로서비스, REST API, AI/머신러닝 백엔드 | 소규모 앱, 간단한 백엔드, 프로토타입 | 복잡한 데이터베이스 기반의 대형 웹 앱 |

## 💻 간단한 코드 예시

FastAPI를 사용하면 단 몇 줄만으로 API 백엔드를 구성할 수 있습니다.


```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}
```

## FastAPI를 사용하는 가장 핵심적인 이유

FastAPI를 사용하는 가장 핵심적인 이유는 파이썬의 생산성을 유지하면서도, Node.js나 Go에 비견되는 압도적인 성능과 자동화된 개발 환경을 제공하기 때문입니다. 구체적인 주요 장점은 다음과 같습니다.

### 1. 압도적인 성능 (고성능 Async)

* Starlette와 Pydantic 기반: 파이썬 웹 프레임워크 중 가장 빠른 축에 속합니다.
* 비동기(Async) 지원: async/await를 완전히 지원하여 대규모 트래픽과 I/O 바운드 작업을 효율적으로 처리합니다.

### 2. 자동 문서화 (Swagger UI)

* 코드 작성 즉시 API 문서 생성: 코드를 짜면 /docs 주소에 대화형 API 문서(Swagger)가 자동으로 만들어집니다.
* 실험 가능: 브라우저에서 바로 API를 테스트하고 결과를 확인할 수 있어 프론트엔드 개발자와의 협업이 매우 빨라집니다.

### 3. 생산성 및 코드 안정성 (Type Hinting)

* 파이썬 타입 힌트 활용: 함수 인자에 타입을 지정하는 것만으로 데이터 검증(Validation)과 직렬화가 자동으로 수행됩니다.
* 에러 감소: 올바르지 않은 데이터가 들어오면 자동으로 422 Unprocessable Entity 에러를 반환합니다.
* 자동 완성 지원: VS Code나 PyCharm 같은 IDE에서 강력한 코드 자동 완성을 제공하여 오타와 버그를 줄여줍니다.

### 4. 간결함과 현대적인 설계

* Flask처럼 쉽고 Django보다 가벼움: 진입 장벽이 낮고, 코드의 양이 Flask/Django에 비해 눈에 띄게 줄어듭니다.
* Dependency Injection (의존성 주입): 데이터베이스 세션 관리나 인증(Auth) 로직을 깔끔하게 모듈화할 수 있는 강력한 시스템을 내장하고 있습니다.

최근 글로벌 개발자 조사(JetBrains 및 Stack Overflow)에 따르면, 현재 파이썬 웹 프레임워크 중 개발자들이 가장 많이 사용하는 것은 FastAPI입니다.
과거에는 Django와 Flask가 양대 산맥을 이루었으나, 최근 수년간 FastAPI가 급격하게 성장하며 누적 점유율 약 38%로 전체 1위를 차지했습니다. 
하지만 단순히 "무엇이 1위인가"보다 "내 프로젝트 성격이 무엇인가"에 따라 개발자들의 선택이 극명하게 갈립니다. 각 프레임워크를 많이 쓰는 상황과 이유를 정리해 드립니다.

---

## 📊 프레임워크별 핵심 요약

| 프레임워크 | 현재 트렌드 및 위치 | 주로 사용하는 상황 | 핵심 장점 |
|---|---|---|---|
| FastAPI | 현재 가장 인기 있는 대세 | 인공지능(AI/ML) 모델 서빙, 마이크로서비스, SPA(React, Vue 등)의 백엔드 | 압도적인 비동기 속도, 자동 문서화(Swagger) |
| Django | 대기업 및 대규모 서비스의 표준 | 어드민 페이지가 필요한 복잡한 웹 서비스, 대규모 커머스, 시니어 개발자가 많은 팀 | 'Batteries Included' (로그인, ORM, 보안 기능 기본 내장) |
| Flask | 레거시 유지보수 및 소규모 툴 | 가벼운 프로토타입, 단발성 자동화 스크립트, 기존 Flask 프로젝트 유지보수 | 가볍고 단순함, 높은 자유도 |

---

## 🛠 개발자들이 상황별로 선택하는 기준 (FastAPI vs. Django vs. Flask)

### 1. FastAPI를 선택하는 경우 (점유율 1위 이유)

* AI/데이터 사이언스 연동: Microsoft, Netflix, Uber 등 글로벌 테크 기업들이 인공지능 모델을 웹 API로 서빙할 때 표준처럼 사용합니다.
* 프론트엔드와 분리된 구조: React, Vue, Svelte, Next.js나 모바일 앱의 '순수 백엔드 API 서버' 역할만 필요할 때 가장 효율적입니다.
* 비동기 처리(Async): 대규모 트래픽이나 실시간 데이터 처리가 중요할 때 Node.js나 Go 언어에 밀리지 않는 성능을 냅니다.

### 2. Django를 선택하는 경우 (여전히 강력한 시장 지배력)

* 빠른 비즈니스 출시(MVP - Minimum Viable Product): 데이터베이스 설계, 로그인/회원가입 기능, 어드민(관리자) 페이지를 따로 만들 시간 없이 빠르게 완성도 높은 서비스를 구축해야 할 때 씁니다.
* 규모가 큰 팀: 프레임워크의 규칙이 매우 엄격하기 때문에, 여러 명의 개발자가 협업해도 코드가 정돈된 상태를 유지하기 쉽습니다.

### 3. Flask를 선택하는 경우 (과거의 1위, 현재는 감소 추세)

* 최소한의 가벼움: 데이터베이스나 복잡한 기능 없이 가볍게 웹페이지 하나 띄우거나, 간단한 장치를 제어하는 API를 만들 때 선택합니다.
* 다만 최신 트렌드에서는: Flask가 하던 '가벼운 API 서버' 역할을 상당 부분 FastAPI가 흡수하면서 신규 프로젝트에서는 채택률이 눈에 띄게 줄었습니다.

### 💡 결론 및 제안

* 새로운 API 프로젝트를 시작하거나, AI/ML 모델을 다룬다면? 무조건 FastAPI를 추천합니다.
* 회원 관리, 게시판, 권한 설정, 관리자 페이지까지 한 번에 다 돌아가는 거대한 웹 서비스를 만든다면? 여전히 Django가 정답입니다.

---

FastAPI에 대해 더 궁금한 점:

* 내 컴퓨터에 첫 FastAPI 프로젝트 설정하는 방법
* 데이터베이스(SQLAlchemy 등) 또는 AI 모델과 연동하는 방법
* 비동기(async/await) 기능을 올바르게 사용하는 방법

---

[1] [https://github.com](https://github.com/fastapi/fastapi)
[2] [https://en.wikipedia.org](https://en.wikipedia.org/wiki/FastAPI)
[3] https://fastapi.tiangolo.com
[4] [https://www.youtube.com](https://www.youtube.com/watch?v=umbU5Pk03CM)
[5] [https://medium.com](https://medium.com/codex/fastapi-the-modern-python-web-framework-that-bridges-performance-and-simplicity-cfc4ab807418)
[6] [https://www.youtube.com](https://www.youtube.com/watch?v=BPRKBQwEHe0&t=102)
[7] [https://www.kern-it.be](https://www.kern-it.be/en/definitions/fastapi/)
[8] [https://www.youtube.com](https://www.youtube.com/shorts/2dHFQqRNjg8)

---

# FastAPI Projet composition

> FastAPI 프로젝트 구성
> * FastAPI 앱 초기화 및 CORS 설정
> * 로컬에서 실행 확인 (예: `uvicorn main:app --reload`)
> * Swagger UI(`/docs`)에서 API 문서 확인 가능

이 3가지 요구사항은 FastAPI 프로젝트를 시작할 때 거치는 가장 표준적이고 핵심적인 초기 설정 단계입니다. 각 항목이 무엇을 의미하고, 코드로 어떻게 구현하는지 알기 쉽게 정리해 드리겠습니다.

---

## 1. FastAPI 앱 초기화 및 CORS 설정

* FastAPI 앱 초기화: FastAPI 프레임워크의 인스턴스(객체)를 생성하여 웹 애플리케이션을 구동할 준비를 하는 것입니다.
* CORS(Cross-Origin Resource Sharing) 설정: 보안상의 이유로 브라우저는 다른 도메인(Origin)에서 오는 API 요청을 기본적으로 차단합니다. 예를 들어, 프론트엔드(http://localhost:3000)가 백엔드(http://localhost:8000)에 데이터를 요청하려면 백엔드에서 "이 도메인의 접근을 허용하겠다"고 명시해야 합니다. 이를 처리해 주는 설정입니다.

## 💻 구현 코드 (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# [1] FastAPI 앱 초기화
app = FastAPI(
    title="My Project API",
    description="FastAPI 프로젝트 초기 설정",
    version="1.0.0"
)
# [2] CORS 설정 (허용할 주소 목록)
origins = [
    "http://localhost:3000",    # React, Next.js 등 프론트엔드 로컬 주소
    "http://127.0.0.1:3000",
    # "*" 를 넣으면 모든 도메인에서의 접근을 허용합니다 (개발 단계에서 편리함)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 허용할 origin 목록
    allow_credentials=True,      # 쿠키나 인증 정보 포함 허용 여부
    allow_methods=["*"],         # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],         # 모든 HTTP 헤더 허용
)

# 테스트용 기본 엔드포인트
@app.get("/")
def read_root():
    return {"status": "success", "message": "FastAPI 서버가 정상 작동 중입니다."}
```

---

## 2. 로컬에서 실행 확인 (uvicorn main:app --reload)

FastAPI는 자체적으로 실행되는 서버가 아니라, Uvicorn이라는 고성능 ASGI 서버 위에서 동작합니다. 터미널에 이 명령어를 입력하면 로컬 컴퓨터에서 서버가 켜집니다.

* `uvicorn`: 서버를 실행하는 프로그램 이름입니다.
* `main:app`: `main.py` 파일 안에 있는 app 이라는 변수(FastAPI 인스턴스)를 찾아 실행하라는 의미입니다. (만약 파일명이 `server.py` 라면 `server:app` 으로 적어야 합니다.)
* `--reload`: 개발용 필수 옵션입니다. 코드를 수정하고 저장할 때마다 서버가 알아서 자동으로 재시작되므로, 매번 서버를 껐다 켤 필요가 없습니다.

## 🚀 실행 순서

   1. 터미널(Terminal)을 열고 `main.py` 파일이 있는 디렉토리로 이동합니다.
   2. 아래 명령어를 입력합니다.
   
   `uvicorn main:app --reload`
   
   3. 성공하면 터미널에 INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit) 같은 문구가 뜹니다.
   4. 브라우저를 열고 http://127.0.0.1:8000 에 접속해서 {"status": "success", ...} 메시지가 잘 나오는지 확인합니다.

---

## 3. Swagger UI (/docs)에서 API 문서 확인

FastAPI의 가장 큰 장점 중 하나로, 개발자가 따로 문서를 작성하지 않아도 소스코드를 분석해 실시간으로 테스트 가능한 API 명세서를 만들어줍니다.

## 🔍 확인 방법

   1. 서버가 켜진 상태(uvicorn 실행 중)에서 브라우저 주소창에 http://127.0.0를 입력하고 접속합니다.
   2. 화면에 여러분이 만든 API 목록(예: GET /)이 깔끔한 UI로 나타납니다.
   3. 원하는 엔드포인트를 클릭한 뒤 [Try it out] ➡️ [Execute] 버튼을 순서대로 누르면, 프론트엔드 코드를 짜지 않고도 실제 백엔드가 어떤 데이터를 리턴하는지 즉시 확인할 수 있습니다.

---

## `fastapi dev main.py` vs. `uvicorn main:app --reload`

Both commands start a FastAPI development server with hot-reloading, but **`fastapi dev main.py`** is the modern, developer-friendly CLI wrapper introduced in FastAPI v0.111.0, whereas **`uvicorn main:app --reload`** is the underlying lower-level ASGI server command.

| Feature | `fastapi dev main.py` | `uvicorn main:app --reload` |
| --- | --- | --- |
| **Tooling** | Official FastAPI CLI wrapper | Direct Uvicorn ASGI server call |
| **Target Syntax** | File path (`main.py`) | Python import path (`main:app`) |
| **Interactive Docs Link** | Automatically highlights local docs URL in logs | Requires manually opening `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)` |
| **Error Syntax Handling** | Catches syntax errors during startup without crashing | Fails to start until the import syntax is valid |
| **Production Counterpart** | `fastapi run main.py` | `uvicorn main:app` |

* **`fastapi dev`** automatically detects your FastAPI instance inside the file (e.g., `app = FastAPI()`), so you point directly to the filename (`main.py`).
* **`uvicorn`** requires explicit module-to-variable target syntax (`module_name:app_variable_name`).
* Under the hood, the `fastapi` CLI uses Uvicorn anyway, adding extra developer-focused defaults like cleaner log formatting and automatic application discovery.

**같은 서버(Uvicorn)를 띄우는 것이며 작동하는 내부 엔진도 완전히 동일**합니다. 다르게 느껴지는 이유는 **명령어를 입력하는 대상(인자)을 지정하는 방식**만 다르기 때문입니다.

두 명령어의 지정 방식 차이는 다음과 같습니다:

* **`fastapi dev main.py` (파이썬 파일 경로 지정)**
* 실제 시스템의 **파일 경로**(`main.py`)를 입력받습니다.
* 실행 시 FastAPI가 파일 내부를 자동으로 스캔해서 `app = FastAPI()` 객체를 찾아낸 뒤 Uvicorn을 실행시켜 줍니다.

* **`uvicorn main:app --reload` (파이썬 모듈 및 변수명 지정)**
* 파이썬의 **임포트(Import) 문법** 경로를 입력받습니다.
* `main`이라는 파이썬 파일(모듈) 안에서 `app`이라는 변수명에 할당된 FastAPI 객체를 직접 지정하여 Uvicorn에 넘겨주는 방식입니다.

* **`fastapi dev main.py`**: "여기 `main.py` 파일 열어서 안에 있는 FastAPI 앱 알아서 실행해 줘." (자동 설정)
* **`uvicorn main:app --reload`**: "`main` 파일 안에 있는 `app`이라는 특정 객체를 직접 가져와서 실행해 줘." (수동 지정)

결과적으로 두 명령어 모두 동일하게 컴퓨터의 **`[http://127.0.0.1:8000](http://127.0.0.1:8000)`** 주소로 동일한 개발 서버를 띄웁니다.

---

## `fastapi dev` vs. `fastapi run`

`fastapi dev`는 **개발 환경(Development)** 용도이고, `fastapi run`은 **운영/배포 환경(Production)** 용도입니다.

두 명령어 모두 FastAPI CLI에서 제공하지만, **자동 새로고침(Hot-Reload)** 여부와 **서버 워커(Worker) 관리 방식**에서 결정적인 차이가 있습니다.

| 구분 | `fastapi dev` | `fastapi run` |
| --- | --- | --- |
| **주요 목적** | 코드 수정 및 디버깅 (개발용) | 실제 서비스 배포 및 제공 (운영용) |
| **코드 변경 감지 (`--reload`)** | **기본 활성화** (코드 수정 시 자동 재시작) | **비활성화** (코드 변경을 감지하지 않음) |
| **바인딩 IP (기본값)** | `127.0.0.1` (내 컴퓨터에서만 접속 가능) | `0.0.0.0` (외부 모든 네트워크 접속 허용) |
| **멀티 프로세스 (Workers)** | 단일 프로세스 실행 | CPU 코어 수에 맞춘 멀티 워커/프로세스 실행 가능 |
| **로그 스타일** | 대화형/시각적으로 다듬어진 디버깅 전용 로그 | 표준 시스템 로그 (배포용 가벼운 포맷) |

* **내 컴퓨터에서 개발 중일 때:** `fastapi dev main.py`를 사용합니다. 코드를 수정하고 저장할 때마다 서버가 자동으로 재시작되어 바로 결과를 확인할 수 있습니다.
* **서버에 실제로 배포할 때:** `fastapi run main.py`를 사용합니다. 보안과 성능을 위해 외부 접속(`0.0.0.0`)을 열고, 코드 감지 리소스 소비를 줄여 안정적으로 요청을 처리합니다.
