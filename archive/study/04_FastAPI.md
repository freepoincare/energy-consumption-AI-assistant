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
FastAPI doesn't reinvent the wheel; it coordinates a powerful stack of underlying tools: [3] 

* Uvicorn: The lightning-fast ASGI server that runs your application and handles raw network requests.
* Starlette: The underlying toolkit that manages routing, cookies, sessions, and asynchronous operations.
* Pydantic: The data-parsing library that enforces data schemas and handles serialization. [2, 4, 5, 6, 8] 

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

@app.get("/")def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")def read_item(item_id: int, q: str = None):
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

@app.get("/")def read_root():
    return {"message": "안녕하세요, 세상!"}

@app.get("/items/{item_id}")def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}
```

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
