# app/services/ai_service.py

`ai_service.py`는 우리 앱에서 **가장 똑똑한 '두뇌'** 역할을 하는 파일입니다. 단순히 질문에 답하는 것을 넘어, **필요할 때 직접 데이터베이스를 조회(Function Calling)**하고, 거짓말을 하지 않도록 **엄격한 규칙(Anti-hallucination)**을 지키며 대화합니다.

---

### 1. 도구 상자 (Function Calling / Tool Use)
AI가 "7월 15일 전기 얼마나 썼어?"라는 질문을 받으면, 단순히 추측하는 게 아니라 **직접 파이썬 함수를 실행**해서 데이터를 찾아옵니다.
*   **`get_energy_data_by_date`**: 특정 날짜의 사용량과 메모를 확인합니다.
*   **`get_energy_data_by_period`**: 특정 기간의 일별 기록을 싹 긁어옵니다.
*   **`get_energy_statistics`**: 특정 기간의 합계, 평균, 최대/최소값을 계산합니다.

### 2. 컨텍스트 주입 (Context Injection) & 시스템 프롬프트
AI에게 대화 시작 전 **"미리 공부할 자료"**를 줍니다.
*   **요약 데이터 주입**: `EnergyDataService`에서 만든 전체 요약본을 AI에게 먼저 읽힙니다. 웬만한 질문은 이 요약본만 보고도 바로 답할 수 있게 하기 위해서죠.
*   **엄격한 규칙 (Anti-hallucination)**: 
    *   "모르는 걸 아는 척하지 마라."
    *   "단위는 무조건 kWh를 써라."
    *   "마크다운(Bold, List 등)을 쓰지 말고 평문으로만 답해라." (UI 깔끔함을 위해)

### 3. 대화 프로세스 (`process_chat`)
사용자가 메시지를 보내면 다음과 같은 순서로 작동합니다.
1.  **요약본 생성**: 현재 DB 상태를 요약합니다.
2.  **프롬프트 조립**: 요약본 + 시스템 규칙 + 사용자 질문을 합칩니다.
3.  **OpenAI 호출**: AI에게 질문을 던집니다.
4.  **도구 실행 (선택)**: 만약 AI가 "데이터 더 필요해!"라고 하면, 위에서 만든 '도구'를 실행해 결과를 다시 AI에게 줍니다.
5.  **최종 답변**: 모든 정보를 종합해 사용자에게 친절하게 답합니다.

---

<details>
<summary>[process_chat 함수 상세 설명 - GPT 5.4 (x1)]</summary>
<br>

1. OpenAI에 질문을 보냄
2. AI가 도구(tool/function)를 쓰고 싶으면 실행해 줌
3. 도구 결과를 다시 AI에게 전달
4. 최종 답변을 받아 저장 후 반환

## 전체 코드
```python
try:
    # Build initial messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.message}
    ]

    tool_calls_log: List[Dict[str, Any]] = []

    # Function Calling loop (max 3 iterations to prevent infinite loops)
    max_iterations = 3
    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=0.1,
            max_tokens=800
        )

        assistant_message = response.choices[0].message

        tool_calls = getattr(assistant_message, "tool_calls", None)

        # If no tool calls, we have the final answer
        if not tool_calls:
            reply = assistant_message.content.strip() if assistant_message.content else ""
            break

        # Process tool calls
        # Append assistant message with tool_calls to conversation
        messages.append({
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })

        for tool_call in assistant_message.tool_calls:
            func_name = tool_call.function.name
            try:
                func_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                func_args = {}

            logger.info(f"Tool call: {func_name}({func_args})")

            # Execute the tool
            executor = TOOL_EXECUTORS.get(func_name)
            if executor:
                result = executor(func_args)
            else:
                result = {"error": f"Unknown tool '{func_name}'."}

            # Log the tool call
            tool_calls_log.append({
                "tool": func_name,
                "arguments": func_args,
                "result": result
            })

            # Append tool result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
    else:
        # If we exhausted iterations, get the last content
        reply = assistant_message.content.strip() if assistant_message.content else "I was unable to complete the analysis. Please try a simpler question."

    # Persist completed chat exchange
    from app.services.conversation_service import ConversationService
    ConversationService.record_chat_exchange(conv_id, request.message, reply)

    return ChatResponse(
        conversation_id=conv_id,
        reply=reply,
        used_summary=True,
        tool_calls_made=tool_calls_log,
        created_at=now_str
    )
```

## 1. `try:`  
```python
try:
```

- 이 아래 코드를 실행하다가 **에러가 발생할 수 있으니 대비**하겠다는 뜻입니다.
- 예를 들어:
  - OpenAI API 호출 실패
  - JSON 파싱 실패
  - tool 실행 중 오류
- 이 블록 안에서 문제가 생기면 아래의 `except`로 이동합니다.

즉, **안전하게 처리하려는 시작점**입니다.


## 2. 초기 메시지 만들기
```python
# Build initial messages
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": request.message}
]
```

이 부분은 OpenAI에게 보낼 **대화 기록(messages)**를 처음 만드는 부분입니다.

### `messages`
- OpenAI Chat API는 대화를 `messages` 배열 형태로 받습니다.
- 각 메시지는 `role`과 `content`를 가집니다.

### 첫 번째 메시지
```python
{"role": "system", "content": system_prompt}
```

- `role: "system"`은 AI의 **행동 규칙**을 정합니다.
- 예:
  - 너는 에너지 분석 도우미다
  - 없는 정보는 지어내지 마라
  - 필요하면 tool을 사용해라
- 즉, AI의 **성격 + 규칙 + 컨텍스트**를 주는 메시지입니다.

### 두 번째 메시지
```python
{"role": "user", "content": request.message}
```

- 사용자가 실제로 입력한 질문입니다.
- 예:
  - `"지난주 평균 사용량 알려줘"`
  - `"2024-07-15 전력 사용량 어땠어?"`

즉, 이 시점의 `messages`는 대략 이런 상태예요:

```python
[
    {"role": "system", "content": "너는 에너지 분석 AI야..."},
    {"role": "user", "content": "지난주 평균 사용량 알려줘"}
]
```

## 3. tool 호출 기록 저장용 리스트
```python
tool_calls_log: List[Dict[str, Any]] = []
```

- tool 호출 내역을 저장할 빈 리스트입니다.
- 나중에 어떤 함수가 호출되었고, 어떤 인자가 들어갔고, 결과가 뭐였는지 기록합니다.

예를 들면 나중에 이런 데이터가 들어갈 수 있어요:

```python
[
    {
        "tool": "get_energy_statistics",
        "arguments": {"start_date": "2024-07-01", "end_date": "2024-07-07"},
        "result": {"average_kwh": 12.5, "total_kwh": 87.5}
    }
]
```

이건 디버깅, 추적, 프론트엔드 표시용으로 매우 유용합니다.


## 4. 최대 반복 횟수 설정
```python
# Function Calling loop (max 3 iterations to prevent infinite loops)
max_iterations = 3
```

- AI가 tool을 호출하고, 그 결과를 보고, 또 다른 tool을 호출할 수도 있습니다.
- 그런데 이게 무한 반복되면 안 되죠.
- 그래서 **최대 3번까지만 반복**하게 제한합니다.

즉:
- 1번 호출하고 끝날 수도 있고
- 2~3번 연속 tool 사용 후 끝날 수도 있음
- 하지만 4번 이상은 못 감

이건 **무한 루프 방지용 안전장치**입니다.


## 5. 반복문 시작
```python
for iteration in range(max_iterations):
```

- `range(max_iterations)`는 `0, 1, 2` 총 3번 반복합니다.
- 매 반복마다:
  1. OpenAI에 현재까지의 대화 기록을 보냄
  2. AI가 최종 답을 주는지 확인
  3. 아니면 tool 요청을 처리함

`iteration` 변수는 현재 몇 번째 반복인지 나타냅니다.
- 1번째: `iteration = 0`
- 2번째: `iteration = 1`
- 3번째: `iteration = 2`


## 6. OpenAI API 호출
```python
response = client.chat.completions.create(
    model=settings.OPENAI_MODEL,
    messages=messages,
    tools=TOOL_DEFINITIONS,
    tool_choice="auto",
    temperature=0.1,
    max_tokens=800
)
```

이 줄이 **실제로 OpenAI에게 요청을 보내는 부분**입니다.

하나씩 보면:

### `model=settings.OPENAI_MODEL`
- 어떤 모델을 사용할지 지정합니다.
- 예: `"gpt-4o-mini"` 같은 값
- 설정 파일에서 불러옵니다.

### `messages=messages`
- 지금까지 쌓인 대화 기록 전체를 보냅니다.
- system + user + assistant + tool 결과까지 포함될 수 있습니다.

### `tools=TOOL_DEFINITIONS`
- AI에게 사용할 수 있는 함수 목록을 알려줍니다.
- 예:
  - `get_energy_data_by_date`
  - `get_energy_statistics`
- 여기서 중요한 점:
  - AI가 함수 자체를 실행하는 건 아님
  - **“이 함수를 호출하고 싶다”라고 요청만 함**
  - 실제 실행은 서버 코드가 합니다

### `tool_choice="auto"`
- AI가 알아서 판단하게 합니다.
- 즉:
  - tool이 필요 없으면 그냥 답변
  - tool이 필요하면 tool call 생성

### `temperature=0.1`
- 답변의 랜덤성(창의성)을 낮춥니다.
- 숫자가 낮을수록 더 안정적이고 일관된 답변을 기대할 수 있습니다.
- 데이터 분석/조회에는 보통 낮은 값이 좋습니다.

### `max_tokens=800`
- 응답 길이 제한입니다.
- 너무 길게 답하지 않도록 제한합니다.


## 7. 첫 번째 응답 메시지 꺼내기
```python
assistant_message = response.choices[0].message
```

- OpenAI 응답에는 보통 `choices`라는 리스트가 있습니다.
- 그중 첫 번째 결과의 `message`를 꺼냅니다.
- 이 `assistant_message` 안에는:
  - AI의 일반 답변(content)
  - 또는 tool 호출 정보(tool_calls)
가 들어있을 수 있습니다.

즉, 이 변수는 “이번 턴에서 AI가 한 말”입니다.


## 8. tool_calls 속성 읽기
```python
tool_calls = getattr(assistant_message, "tool_calls", None)
```

- `assistant_message.tool_calls`가 있으면 가져오고
- 없으면 `None`을 반환합니다.

### 왜 `getattr` 사용?
만약 그냥:
```python
assistant_message.tool_calls
```
라고 했는데 `tool_calls` 속성이 없으면 에러가 날 수 있습니다.

`getattr(..., None)`은 안전하게 읽는 방법입니다.

즉:
- tool 요청이 있으면 `tool_calls`에 들어감
- 없으면 `None`


## 9. tool 호출이 없으면 최종 답변
```python
# If no tool calls, we have the final answer
if not tool_calls:
    reply = assistant_message.content.strip() if assistant_message.content else ""
    break
```

이건 아주 중요합니다.

### `if not tool_calls:`
- AI가 tool을 요청하지 않았다면
- 이미 최종 답변을 했다는 뜻입니다

### `assistant_message.content.strip()`
- 응답 텍스트 앞뒤 공백 제거
- 예:
  - `"  지난주 평균은 12.3kWh입니다.  "`
  - → `"지난주 평균은 12.3kWh입니다."`

### `if assistant_message.content else ""`
- 혹시 content가 없으면 빈 문자열로 처리
- `None.strip()` 에러를 막습니다

### `break`
- 반복문을 즉시 종료합니다.
- 즉, “이제 더 이상 tool 실행 안 해도 된다”는 뜻입니다.


## 10. tool 호출 처리 시작
```python
# Process tool calls
# Append assistant message with tool_calls to conversation
messages.append({
    "role": "assistant",
    "content": assistant_message.content or "",
    "tool_calls": [
        {
            "id": tc.id,
            "type": "function",
            "function": {
                "name": tc.function.name,
                "arguments": tc.function.arguments
            }
        }
        for tc in assistant_message.tool_calls
    ]
})
```

이 부분은 AI가 “함수를 호출하고 싶다”고 한 내용을 **대화 기록에 추가**하는 부분입니다.

왜 필요할까요?

OpenAI function calling은 다음 흐름을 따릅니다:

1. AI: `"get_energy_statistics"` 함수를 호출하고 싶어요
2. 서버: 실제로 함수 실행
3. 서버: 함수 결과를 다시 messages에 넣음
4. AI: 그 결과를 보고 최종 답변 작성

그런데 이 흐름을 유지하려면,  
AI가 “어떤 함수를 호출하려 했는지”도 messages에 남겨야 합니다.

### `messages.append(...)`
- 기존 대화 뒤에 새로운 메시지를 추가합니다.

### `"role": "assistant"`
- 이 메시지는 AI가 한 말입니다.

### `"content": assistant_message.content or ""`
- AI가 content를 함께 보냈으면 저장
- 없으면 빈 문자열
- function calling에서는 content 없이 tool_calls만 오는 경우도 많습니다

### `"tool_calls": [...]`
- AI가 요청한 함수 목록을 넣습니다

#### 리스트 컴프리헨션
```python
for tc in assistant_message.tool_calls
```
- tool call이 여러 개일 수도 있어서 반복하면서 변환합니다.

#### 각 tool call 정보
```python
{
    "id": tc.id,
    "type": "function",
    "function": {
        "name": tc.function.name,
        "arguments": tc.function.arguments
    }
}
```

- `id`: 이 tool call의 고유 ID
- `type`: 함수 호출이라는 뜻
- `name`: 호출할 함수 이름
- `arguments`: 함수에 넘길 인자(JSON 문자열)

예를 들면 이렇게 저장될 수 있어요:
```python
{
    "role": "assistant",
    "content": "",
    "tool_calls": [
        {
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "get_energy_statistics",
                "arguments": "{\"start_date\":\"2024-07-01\",\"end_date\":\"2024-07-07\"}"
            }
        }
    ]
}
```


## 11. 각 tool call 반복 처리
```python
for tool_call in assistant_message.tool_calls:
```

- AI가 요청한 tool들을 하나씩 처리합니다.
- 보통 1개겠지만, 여러 개일 가능성도 있으므로 반복문 사용


## 12. 함수 이름 꺼내기
```python
func_name = tool_call.function.name
```

- AI가 호출하려는 함수 이름을 꺼냅니다.
- 예:
  - `"get_energy_data_by_date"`
  - `"get_energy_statistics"`

## 13. 함수 인자 JSON 파싱
```python
try:
    func_args = json.loads(tool_call.function.arguments)
except json.JSONDecodeError:
    func_args = {}
```

### `tool_call.function.arguments`
- 함수 인자는 보통 JSON 문자열 형태입니다.
- 예:
```python
'{"date": "2024-07-15"}'
```

### `json.loads(...)`
- JSON 문자열을 파이썬 딕셔너리로 변환합니다.
- 결과:
```python
{"date": "2024-07-15"}
```

### 왜 `try-except`?
AI가 잘못된 JSON을 만들 가능성도 아주 약간 있습니다.

예:
```python
'{date: 2024-07-15}'
```
이건 올바른 JSON이 아닙니다.

그럴 때 `json.JSONDecodeError`가 발생하므로,
에러 대신 그냥 빈 딕셔너리 `{}`를 넣어 처리합니다.

즉, **입력 파싱 방어 코드**입니다.

## 14. 로그 출력
```python
logger.info(f"Tool call: {func_name}({func_args})")
```

- 서버 로그에 어떤 함수가 어떤 인자로 호출되었는지 남깁니다.
- 디버깅할 때 매우 중요합니다.

예:
```python
Tool call: get_energy_statistics({'start_date': '2024-07-01', 'end_date': '2024-07-07'})
```

## 15. 실행할 함수 찾기
```python
# Execute the tool
executor = TOOL_EXECUTORS.get(func_name)
```

- `TOOL_EXECUTORS`는 보통 **함수 이름 → 실제 실행 함수**를 연결한 딕셔너리입니다.

예:
```python
TOOL_EXECUTORS = {
    "get_energy_data_by_date": get_energy_data_by_date,
    "get_energy_statistics": get_energy_statistics
}
```

따라서:
- `func_name = "get_energy_statistics"`면
- `executor`는 실제 파이썬 함수 객체가 됩니다

## 16. 함수 실행 또는 에러 결과 생성
```python
if executor:
    result = executor(func_args)
else:
    result = {"error": f"Unknown tool '{func_name}'."}
```

### `if executor:`
- 해당 이름의 함수가 실제로 등록되어 있으면 실행

### `result = executor(func_args)`
- 실제 함수 호출
- `func_args`를 넘겨서 실행 결과를 받음

예:
```python
result = {"average_kwh": 12.5, "total_kwh": 87.5}
```

### `else`
- 등록되지 않은 함수 이름이면 실행할 수 없음

### 에러 결과
```python
{"error": "Unknown tool '...'."}
```

이렇게 하면 서버가 터지지 않고, AI에게 “그 함수는 없음”이라고 결과를 줄 수 있습니다.

좋은 방어 코드예요.

## 17. tool 호출 로그 저장
```python
# Log the tool call
tool_calls_log.append({
    "tool": func_name,
    "arguments": func_args,
    "result": result
})
```

- 어떤 tool이 호출되었는지 기록 리스트에 추가합니다.
- 나중에 API 응답에 포함할 수도 있고, 디버깅에도 사용합니다.

예:
```python
{
    "tool": "get_energy_statistics",
    "arguments": {"start_date": "2024-07-01", "end_date": "2024-07-07"},
    "result": {"average_kwh": 12.5, "total_kwh": 87.5}
}
```

## 18. tool 실행 결과를 대화에 추가
```python
# Append tool result to conversation
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": json.dumps(result)
})
```

<br>
</details>

---

<details>
<summary>[process_chat 함수 상세 설명 - gemini 3 flash (x0.5)]</summary>
<br>

이 코드는 **OpenAI의 'Function Calling(함수 호출)'** 기능을 활용하여 AI가 단순히 말을 하는 것을 넘어, **실제로 데이터를 조회하고 분석하는 '행동'을 수행하게 만드는 핵심 로직**입니다.

---

### 1. 대화의 시작 (Initial Messages)
```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": request.message}
]
```
*   **System**: AI에게 "너는 에너지 전문가야, 이 데이터를 참고해"라는 지침을 줍니다.
*   **User**: 사용자가 보낸 질문(예: "어제 전기 얼마나 썼어?")을 넣습니다.

### 2. 생각하고 행동하는 루프 (The Loop)
가장 흥미로운 부분입니다. `for iteration in range(max_iterations):` (최대 3번) 루프를 돕니다. 왜 루프를 돌까요?

1.  **질문 던지기**: AI에게 질문과 함께 "사용할 수 있는 도구(TOOL_DEFINITIONS)" 목록을 보냅니다.
2.  **AI의 판단**: 
    *   **답변형**: "어제는 10kWh 썼네요." (도구 필요 없음 → `break`로 루프 탈출)
    *   **행동형**: "어제 데이터를 확인해야겠군. `get_energy_data_by_date` 함수를 실행해줘!" (`tool_calls` 발생)

### 3. 도구 실행 과정 (Tool Execution)
AI가 도구를 쓰겠다고 하면, 코드는 다음과 같이 움직입니다.

*   **기록하기**: AI가 "나 이 함수 쓸래"라고 말한 내용을 대화 기록(`messages`)에 추가합니다.
*   **실제 함수 호출**: 
    ```python
    executor = TOOL_EXECUTORS.get(func_name)
    result = executor(func_args) # 실제 파이썬 함수 실행!
    ```
    `TOOL_EXECUTORS`라는 지도에서 함수 이름을 찾아 실제로 실행하고 결과를 가져옵니다.
*   **결과 보고**: 실행 결과(데이터)를 다시 `messages`에 추가합니다. 이때 역할은 **`role: "tool"`**입니다.

### 4. 다시 AI에게 물어보기 (Next Iteration)
이제 `messages`에는 **[질문 + AI의 도구 요청 + 실제 데이터 결과]**가 모두 들어있습니다. 루프의 처음으로 돌아가 이 전체 기록을 다시 OpenAI에게 보냅니다. 
그러면 AI는 **"아, 아까 요청한 데이터를 받았구나! 이걸 보니 어제는 10kWh를 썼네."**라고 최종 답변을 할 수 있게 됩니다.

### 5. 대화 저장 및 마무리 (Persistence)
```python
ConversationService.record_chat_exchange(conv_id, request.message, reply)
```
*   AI의 최종 답변이 나오면, 사용자의 질문과 AI의 답변을 DB에 저장합니다. 그래야 나중에 '대화 기록' 메뉴에서 다시 볼 수 있겠죠?

### 6. 안전장치 (Exception & Fallback)
```python
except Exception as e:
    reply = cls._generate_mock_or_offline_reply(request.message, summary_data)
```
*   만약 인터넷이 끊기거나 OpenAI 서버가 점검 중이라면? 앱이 뻗어버리는 대신, 미리 준비된 **'오프라인 답변 생성기'**가 작동하여 최소한의 정보를 제공합니다. (매우 친절한 설계죠!)

---

### 💡 비유로 이해하기 (식당 시나리오)

1.  **손님(User)**: "오늘 추천 메뉴(어제 사용량)가 뭐예요?"
2.  **웨이터(AI)**: (메뉴판에 없네?) "잠시만요, **주방(Tool)**에 물어보고 올게요."
3.  **매니저(Loop)**: 주방에 가서 "오늘 추천 메뉴 뭐야?"라고 묻고 **대답(Result)**을 듣습니다.
4.  **웨이터(AI)**: "주방에서 오늘 스테이크가 좋대요! **추천 메뉴는 스테이크입니다(Final Reply).**"
5.  **기록(Service)**: 오늘 손님이 추천 메뉴를 물어봤고 스테이크라고 답했다고 장부에 적습니다.

### 🌟 이 코드의 핵심 포인트
*   **`max_iterations = 3`**: AI가 무한 루프에 빠져 비용이 계속 나가는 것을 방지하는 안전벨트입니다.
*   **`tool_choice="auto"`**: AI가 스스로 도구를 쓸지 말지 결정하게 합니다.
*   **`role: "tool"`**: AI에게 "이건 내가 지어낸 게 아니라, 실제 시스템에서 조회해온 진짜 데이터야"라고 알려주는 신호입니다.

이 루프 덕분에 우리 앱의 AI는 단순한 챗봇이 아니라, **실제 내 에너지 데이터를 조회하고 분석할 줄 아는 똑똑한 비서**가 되는 것입니다! 이해가 쏙쏙 되시나요? 😊✨

<br>
</details>

### 4. 방어적 설계 (Offline Fallback)
만약 OpenAI API 키가 없거나 인터넷이 안 되면 어떻게 될까요?
*   **`_generate_mock_or_offline_reply`**: 이 함수가 작동합니다. AI 없이도 미리 준비된 규칙(Rule-based)에 따라 요약 데이터를 바탕으로 답변을 만들어냅니다. 앱이 어떤 상황에서도 멈추지 않게 하는 아주 중요한 장치입니다.

---

### 💡 비유로 이해하기
이 파일은 **"데이터 분석가 자격증이 있는 비서"**와 같습니다.
1.  **비서(AI)**는 기본적으로 내 에너지 요약 보고서를 들고 있습니다.
2.  내가 "지난주 평균 어때?"라고 물으면 보고서를 보고 바로 답합니다.
3.  만약 내가 "작년 내 생일엔 어땠어?"라고 물으면, 비서는 **"잠시만요, 창고(DB) 가서 장부 좀 보고 올게요"**라며 도구(`get_energy_data_by_date`)를 사용해 정확한 숫자를 알아옵니다.
4.  절대 대충 "많이 썼을걸요?"라고 **거짓말하지 않도록** 훈련받았습니다.

### 🌟 한 줄 요약
**"사용자의 질문을 분석해 필요한 데이터를 직접 조회하고, 정해진 규칙에 따라 정확한 답변을 생성하는 AI 서비스 계층"**입니다.

이 코드가 있어서 우리 앱이 단순한 차트 앱을 넘어 **'나만의 에너지 컨설턴트'**가 되는 것이죠!