
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
    allow_origins=origins,       # 허용할 오리진 목록
    allow_credentials=True,     # 쿠키나 인증 정보 포함 허용 여부
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

------------------------------
이 요구사항들을 실제로 구현하기 위해 필요한 파이썬 가상환경(venv) 설정과 필요한 패키지(fastapi, uvicorn) 설치 명령어부터 차근차근 안내해 드릴까요? 아니면 바로 코드를 작성하는 단계로 넘어가시겠어요?

