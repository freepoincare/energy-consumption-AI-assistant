# Uvicorn

Source: https://wikidocs.net/228062

Uvicorn은 초고속 비동기 처리를 목표로 설계된 파이썬의 가장 대중적인 ASGI(Asynchronous Server Gateway Interface) 서버입니다.

FastAPI, Starlette, Quart와 같은 현대적인 비동기 웹 프레임워크들의 단짝이자, 2026년 현재 파이썬 웹 개발 입문자가 가장 먼저 접하게 되는 표준 서버 엔진입니다.

Uvicorn(유비콘)은 FastAPI 같은 현대적인 파이썬 웹 애플리케이션을 구동하는 번개처럼 빠른 웹 서버(ASGI 서버)입니다.
FastAPI로 코드를 아무리 잘 짜도, 인터넷에서 들어오는 사용자의 요청(HTTP 요청)을 받아서 파이썬 코드로 전달해 주는 '서버 프로그램'이 필요한데, 그 역할을 하는 것이 바로 Uvicorn입니다.

## 2026년 기준 실무 동향: "비동기 웹의 심장이자 엔진"

과거에는 속도 하면 `uvloop`를 따로 깔아야 했으나, 2026년 현재 Uvicorn은 최적화가 극한에 달해 기본 설정만으로도 타 언어(Go, Node.js)에 육박하는 강력한 동시 처리 능력을 보여줍니다.

1. 비동기 I/O의 승리: 수만 명의 사용자가 동시에 접속하여 DB 조회를 기다리는 상황에서도, CPU를 놀리지 않고 효율적으로 다음 요청을 처리하는 비동기 루프 기술의 정점에 서 있습니다.
2. 개발 생산성 1위: `--reload` 옵션 하나로 코드를 수정하는 즉시 서버에 반영되는 쾌적한 개발 경험을 제공하며, 2026년 AI 코딩 도구들과 가장 완벽하게 호환됩니다.
3. HTTP/2 및 WebSocket 지원: 단순히 데이터만 주고받는 것을 넘어, 실시간 채팅이나 스트리밍 웹 서비스를 위한 인프라 기능을 완벽하게 기본 탑재하고 있습니다.

## 주요 특징

* 초고속 엔진 (`uvloop` 및 `httptools`): 내부적으로 C언어로 작성된 고성능 라이브러리들을 활용하여 파이썬의 태생적 한계를 극복했습니다.
* 가벼운 코드베이스: 불필요한 기능 없이 오직 '요청 처리'에만 집중하여 서버 리소스를 극도로 적게 소모합니다.
* 강력한 호환성: 모든 ASGI 호환 프레임워크를 수용하며, `Gunicorn` 워커로 투입될 때 최고의 안정성을 발휘합니다.

## 설치 방법

```bash
uv add uvicorn
```

## 예제 코드: FastAPI와 함께 띄우기

가장 일반적인 현대적 파이썬 웹 구동 방식입니다.

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def welcome():
    return {"message": "2026년 비동기 파이썬 월드에 오신 것을 환영합니다!"}

# 로컬 개발 시 실행 방법 (코드 내부에서 호출)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

## 결론

"파이썬 웹은 느리다"라는 편견을 완전히 박살 낸 주역이 바로 Uvicorn입니다. 2026년 현재 당신이 비동기 파이썬 프레임워크를 선택했다면, 그 엔진룸에는 무조건 Uvicorn이 자리 잡고 있어야 합니다. 가장 빠르고, 가장 가벼우며, 가장 믿음직한 엔진입니다.

---

# Uvicorn 실행 명령어 가이드

FastAPI 애플리케이션을 구동하기 위한 Uvicorn 핵심 실행 명령어.    

## 1. 기본 실행 명령어

```bash
uvicorn main:app --reload
```

## 2. 옵션별 상세 설명
 
* `main:app`: 실행할 파일명과 FastAPI 인스턴스 이름입니다.
* `main`: main.py 파일 파일명을 의미합니다.
   * `app`: 파일 내부의 app = FastAPI() 객체 변수명을 의미합니다.
* `--reload`: 개발용 필수 옵션. 코드를 수정하고 저장하면 서버가 자동으로 재시작됨. (운영 환경에서는 제외)
* `--host 0.0.0.0`: 외부 접속을 허용합니다. (기본값: 127.0.0.1 로컬 접속만 허용)
* `--port 8000`: 서버가 사용할 포트 번호를 지정합니다. (기본값: 8000)

## 3. 실무 추천 명령어 (다양한 조합)

로컬 개발용 (종합):
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

```bash
uvicorn app.main:app --reload --port 8000
```
* `app.`: `app\` 디렉토리 내부
* `main`: main.py 파일명
* `:app`: 파일 내부의 app = FastAPI() 객체 변수명

운영(Production) 배포용 (자동 재시작 해제, 성능 최적화):
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```
* --workers 4: CPU 코어 수에 맞춰 여러 프로세스를 띄워 트래픽 처리량을 높입니다.

## 🚀 로컬 확인 주소

* http://localhost:8000/
    * `Welcome to Electricity Consumption AI Assistant API...` 환영 메시지가 JSON 형태로 출력됨.
* http://localhost:8000/health
    * 서비스의 현재 환경(development)과 상태가 정상(healthy)인지 확인하는 데이터가 출력됨.
* http://localhost:8000/docs (가장 중요 ⭐)
    * `Swagger UI` 페이지가 열립니다. 여기서 `/health`와 `/` API를 직접 테스트해 볼 수 있음.

---

* 전력 소비 데이터를 처리하거나 AI(OpenAI) 기능을 붙이기 위한 새로운 API 주소(Route) 추가 방법을 알아볼까요?
* 터미널에 뜬 로그(Log) 중에서 에러 메시지나 이해하기 어려운 부분이 있어 분석이 필요하신가요?

---

# Uvicorn ASGI server

Uvicorn(유비콘)은 FastAPI 같은 현대적인 파이썬 웹 애플리케이션을 구동하는 번개처럼 빠른 웹 서버(ASGI 서버)입니다.
FastAPI로 코드를 아무리 잘 짜도, 인터넷에서 들어오는 사용자의 요청(HTTP 요청)을 받아서 파이썬 코드로 전달해 주는 '서버 프로그램'이 필요한데, 그 역할을 하는 것이 바로 Uvicorn입니다.
이해하기 쉽게 핵심 특징들을 비유와 함께 설명해 드릴게요.

## 1. 왜 "고성능" 일까요? (C언어급 속도)

Uvicorn이 빠른 이유는 내부적으로 C언어로 작성된 초고속 라이브러리들(uvloop와 httptools)을 사용하기 때문입니다.

* uvloop: 파이썬의 기본 이벤트 루프(작업 스케줄러)를 대체하는 라이브러리로, NodeJS보다 2~4배 더 빠르게 작업을 처리할 수 있도록 도와줍니다.
* httptools: 고성능 C언어 기반 웹 서버인 'Nginx'의 HTTP 파서(해석기)를 가져와 사용하므로, 들어오는 요청을 엄청나게 빠른 속도로 해석합니다.

## 2. ASGI 서버란 무엇인가요? (동시 처리의 달인)

전통적인 파이썬 웹 프레임워크(Flask, Django 등)는 WSGI(위스기)라는 서버 표준을 사용했습니다. 반면 FastAPI와 Uvicorn은 ASGI(아스기)라는 새로운 표준을 사용합니다. 이 둘의 차이는 '식당의 서빙 방식'으로 이해하면 쉽습니다.

* WSGI (과거 방식 - 동기식): 직원이 한 손님의 주문을 받고, 주방에서 요리가 나올 때까지 그 테이블 앞에 가만히 서서 기다립니다. 요리가 나와야만 다음 손님의 주문을 받으러 갈 수 있습니다. (요청이 밀리면 서버가 느려짐)
* ASGI (현재 방식 - 비동기식): 직원이 첫 번째 손님의 주문을 받아 주방에 넘긴 뒤, 요리가 나오는 동안 기다리지 않고 바로 두 번째, 세 번째 손님의 주문을 받으러 갑니다. 요리가 완성되면 그때 손님에게 가져다줍니다.

이 ASGI 방식 덕분에 Uvicorn은 동시에 수천, 수만 명이 접속해도 서버가 멈추지 않고 효율적으로 요청을 처리할 수 있습니다. 실시간 채팅(WebSockets)이나 알림 기능도 끊김 없이 가능한 이유가 바로 이 때문입니다.

## 3. 개발할 때 편리한 기능: --reload

앞서 요구사항에서 보셨던 `uvicorn main:app --reload` 명령어에서, Uvicorn은 소스코드를 실시간으로 감시하는 역할도 합니다. 코드를 고치고 Ctrl + S로 저장하면, Uvicorn이 이를 알아채고 0.1초 만에 서버를 자동으로 재시작해 줍니다.

---

## 요약하자면 💡

* FastAPI = 요리를 만드는 주방장 (애플리케이션 로직)
* Uvicorn = 손님의 주문을 초고속으로 받고 전달하는 지배인 (웹 서버)

둘이 함께 일해야 비로소 완벽한 웹 서비스가 작동하게 됩니다.
Uvicorn에 대해 더 궁금한 점이 있으신가요? 아니면 이제 이 Uvicorn을 활용해 실제 프로젝트 폴더를 만들고 실행하는 실습을 시작해 볼까요?

---

## Resources

* [Mastering Gunicorn and Uvicorn: The Right Way to Deploy FastAPI Applications](https://medium.com/@iklobato/mastering-gunicorn-and-uvicorn-the-right-way-to-deploy-fastapi-applications-aaa06849841e)