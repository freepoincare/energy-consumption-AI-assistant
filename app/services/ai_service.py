"""
AI Chat Service with Context Injection and Function Calling (Tool Use).

Orchestrates:
1. Retrieval of current energy summary from Firestore data via EnergyDataService.
2. Building an anti-hallucination System Prompt with injected JSON summary context.
3. Querying OpenAI Chat Completions API with Function Calling tools.
4. Executing tool calls against the backend service layer (never direct Firestore access).
5. Returning tool results to GPT for final answer generation.

Design Principle:
- Context Injection (summary) remains the DEFAULT.
- Function Calling is used ONLY when the summary is insufficient
  (e.g., specific date lookups, custom date ranges, memo-based investigation).
"""

import json
import logging
import uuid
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from app.core.config import settings
from app.models.chat_models import ChatRequest, ChatResponse
from app.services.data_service import EnergyDataService, repository

logger = logging.getLogger("app.services.ai_service")


# ---------------------------------------------------------------------------
# OpenAI Function Calling Tool Definitions
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_energy_data_by_date",
            "description": (
                "Retrieves the actual daily electricity consumption record for a specified date. "
                "Returns the date, consumption_kwh, and memo if available. "
                "Use this when the user asks about a specific day's consumption that is NOT in the summary."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date to look up in YYYY-MM-DD format (e.g. '2026-07-15')"
                    }
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_energy_data_by_period",
            "description": (
                "Retrieves daily electricity records for a specified date range (inclusive). "
                "Returns total_consumption_kwh, average_daily_consumption_kwh, and the list of daily records with date, consumption_kwh, and memo. "
                "Use this when the user asks about consumption over a custom date range, day-by-day records, "
                "or wants to investigate changes over time that the summary cannot answer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date of the range in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date of the range in YYYY-MM-DD format"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_energy_statistics",
            "description": (
                "Calculates deterministic statistics (total_consumption_kwh, average_daily_consumption_kwh, minimum, maximum, count) for a specific date range. "
                "Use this whenever the user asks for total, average, or summary consumption over a custom date range (e.g. 'between June 1 and June 15', 'first two weeks of August')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date of the range in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date of the range in YYYY-MM-DD format"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        }
    }
]


# ---------------------------------------------------------------------------
# Tool Argument Validation
# ---------------------------------------------------------------------------

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_PERIOD_DAYS = 366  # Reasonable upper limit for date range queries


def _validate_date(date_str: str) -> str:
    """Validates a single date string. Returns error message or empty string."""
    if not DATE_PATTERN.match(date_str):
        return f"Invalid date format '{date_str}'. Expected YYYY-MM-DD."
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return f"Invalid calendar date '{date_str}'."
    return ""


def _get_dataset_bounds() -> tuple:
    """Returns (min_date_str, max_date_str) from the dataset."""
    all_records = repository.get_all()
    if not all_records:
        return ("", "")
    dates = sorted([r["date"] for r in all_records if "date" in r])
    return (dates[0], dates[-1]) if dates else ("", "")


def _validate_date_in_range(date_str: str) -> str:
    """Validates that a date falls within the dataset boundary."""
    min_date, max_date = _get_dataset_bounds()
    if not min_date:
        return "No data available in the dataset."
    if date_str < min_date or date_str > max_date:
        return f"Date '{date_str}' is outside the available dataset period ({min_date} to {max_date})."
    return ""


def _validate_period(start_date: str, end_date: str) -> str:
    """Validates a date range. Returns error message or empty string."""
    err = _validate_date(start_date)
    if err:
        return err
    err = _validate_date(end_date)
    if err:
        return err
    if start_date > end_date:
        return f"start_date '{start_date}' must be on or before end_date '{end_date}'."
    # Check span
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")
    if (d2 - d1).days > MAX_PERIOD_DAYS:
        return f"Date range exceeds maximum allowed span of {MAX_PERIOD_DAYS} days."
    return ""


# ---------------------------------------------------------------------------
# Tool Execution Functions
# ---------------------------------------------------------------------------

def execute_get_energy_data_by_date(args: Dict[str, Any]) -> Dict[str, Any]:
    """Executes get_energy_data_by_date tool with full validation."""
    date_str = args.get("date", "")

    # Validate date format
    err = _validate_date(date_str)
    if err:
        return {"error": err}

    # Validate date in dataset range
    err = _validate_date_in_range(date_str)
    if err:
        return {"error": err}

    # Retrieve record via existing service layer (never direct Firestore)
    record = repository.get_by_id(date_str)
    if not record:
        return {"error": f"No energy record found for date '{date_str}'."}

    return {
        "date": record.get("date", date_str),
        "consumption_kwh": record.get("value"),
        "memo": record.get("memo")
    }


def execute_get_energy_data_by_period(args: Dict[str, Any]) -> Dict[str, Any]:
    """Executes get_energy_data_by_period tool with full validation."""
    start_date = args.get("start_date", "")
    end_date = args.get("end_date", "")

    # Validate period
    err = _validate_period(start_date, end_date)
    if err:
        return {"error": err}

    # Retrieve all records and filter by date range
    all_records = repository.get_all()
    filtered = [
        {
            "date": r.get("date"),
            "consumption_kwh": r.get("value"),
            "memo": r.get("memo")
        }
        for r in all_records
        if start_date <= r.get("date", "") <= end_date
    ]

    if not filtered:
        return {
            "error": f"No energy records found for the period {start_date} to {end_date}.",
            "records_count": 0
        }

    values = [r["consumption_kwh"] for r in filtered if r.get("consumption_kwh") is not None]
    total_kwh = round(sum(values), 4) if values else 0.0
    avg_kwh = round(total_kwh / len(values), 4) if values else 0.0

    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "records_count": len(filtered),
        "total_consumption_kwh": total_kwh,
        "average_daily_consumption_kwh": avg_kwh,
        "records": filtered
    }


def execute_get_energy_statistics(args: Dict[str, Any]) -> Dict[str, Any]:
    """Executes get_energy_statistics tool with full validation."""
    start_date = args.get("start_date", "")
    end_date = args.get("end_date", "")

    # Validate period
    err = _validate_period(start_date, end_date)
    if err:
        return {"error": err}

    # Retrieve and filter records
    all_records = repository.get_all()
    filtered = [
        r for r in all_records
        if start_date <= r.get("date", "") <= end_date
    ]

    if not filtered:
        return {
            "error": f"No energy records found for the period {start_date} to {end_date}.",
            "records_count": 0
        }

    values = [r.get("value", 0) for r in filtered]
    total = round(sum(values), 4)
    count = len(values)
    average = round(total / count, 4) if count > 0 else 0
    minimum = round(min(values), 4)
    maximum = round(max(values), 4)
    min_date = next(r["date"] for r in filtered if r.get("value") == min(values))
    max_date = next(r["date"] for r in filtered if r.get("value") == max(values))

    # Collect memos in the period
    memos = [
        {"date": r.get("date"), "memo": r.get("memo")}
        for r in filtered
        if r.get("memo")
    ]

    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "records_count": count,
        "total_consumption_kwh": total,
        "average_daily_consumption_kwh": average,
        "minimum": {"date": min_date, "consumption_kwh": minimum},
        "maximum": {"date": max_date, "consumption_kwh": maximum},
        "memos_in_period": memos if memos else None
    }


# Tool dispatch table
TOOL_EXECUTORS = {
    "get_energy_data_by_date": execute_get_energy_data_by_date,
    "get_energy_data_by_period": execute_get_energy_data_by_period,
    "get_energy_statistics": execute_get_energy_statistics,
}


# ---------------------------------------------------------------------------
# System Prompt Builder
# ---------------------------------------------------------------------------

def build_system_prompt(summary_data: Dict[str, Any]) -> str:
    """
    Constructs the system prompt with strict anti-hallucination rules and injected energy summary.
    Now includes instructions for Function Calling tool selection.
    """
    summary_json_str = json.dumps(summary_data, indent=2)

    prompt = f"""You are an intelligent, precise AI personal electricity-consumption assistant.
Your goal is to answer the user's questions about their historical electricity usage data accurately.

=== ENERGY CONSUMPTION SUMMARY CONTEXT ===
{summary_json_str}
==========================================

TOOL SELECTION RULES (Context Injection vs Function Calling):
1. ALWAYS check the summary context above FIRST.
2. If the summary contains enough information to answer the question, answer directly WITHOUT calling any tool.
3. Only call a tool when the summary is genuinely insufficient — e.g., for a specific date's consumption, a custom date range, or memo-based investigation.
4. Use get_energy_data_by_date when the user asks about a specific day's consumption or memo.
5. Use get_energy_statistics when the user asks about total, average, or summary consumption over a custom date range (e.g. 'between June 1 and June 15', 'first two weeks of August'). Rely directly on the returned pre-calculated 'total_consumption_kwh' and 'average_daily_consumption_kwh'. Do NOT manually sum the individual daily numbers.
6. Use get_energy_data_by_period when the user asks for individual daily records over a custom date range or wants to investigate day-by-day changes over time. If using get_energy_data_by_period for totals, always use the pre-calculated 'total_consumption_kwh' field returned by the tool.

STRICT ANTI-HALLUCINATION RULES:
1. Rely ONLY on the information provided in the summary above or retrieved via tool calls.
2. Do NOT fabricate, invent, or extrapolate numeric values, dates, trends, averages, or costs.
3. When the user asks about a specific month (e.g. "July 2026", "2026-07", "7월"), check the 'monthly.monthly_breakdown' section in the summary. If that month exists in 'monthly_breakdown', answer with that specific month's metrics (total_consumption_kwh, average_daily_consumption_kwh, days_count) instead of giving the overall period average.
4. If a user asks about dates outside the analysis period ({summary_data.get('period', {}).get('start_date', '2026-03-01')} to {summary_data.get('period', {}).get('end_date', '2026-08-31')}), clearly state that data is only available for the recorded period.
5. Always use "kWh" or "kWh/day" as the unit for electricity consumption.
6. If discussing costs, clearly state that the cost values are "estimated costs" based on unit rates and do NOT represent confirmed or final utility bills.
7. Do not infer a missing value as zero or make assumptions about unlisted metrics.
8. Do NOT claim appliance-level electricity consumption. This dataset represents whole-home electricity consumption.
9. When relating memo information to consumption changes, use cautious language:
   - "This coincides with your note that..."
   - "This may be related to..."
   - "The data shows an increase around this time..."
   - "The electricity data alone cannot prove that [specific appliance] caused the increase."

RESPONSE STYLE:
- Maintain a helpful, polite, and data-grounded tone.
- Answer in the same language as the user's question (e.g. Korean if asked in Korean, English if asked in English).
- PLAIN TEXT ONLY: Do NOT use markdown formatting (no bold '**', italics, headers '#', bullet points '-', or numbered lists) and do NOT use LaTeX math formulas (no \frac, \text, \[, \], etc.).
- CONCISE DIRECT ANSWERS: Provide the direct final answer clearly and cleanly if possible.
"""
    return prompt


# ---------------------------------------------------------------------------
# AI Chat Service
# ---------------------------------------------------------------------------

class AIChatService:
    @staticmethod
    def _get_openai_client():
        try:
            from openai import OpenAI
            if not settings.OPENAI_API_KEY:
                return None
            return OpenAI(api_key=settings.OPENAI_API_KEY)
        except ImportError:
            logger.warning("openai package not installed.")
            return None

    @classmethod
    async def process_chat(cls, request: ChatRequest) -> ChatResponse:
        """
        Executes the context-injected chat flow with Function Calling support.

        Flow:
        1. Build system prompt with injected summary context
        2. Send to OpenAI with tool definitions
        3. If GPT returns tool_calls, execute them and send results back
        4. Return final answer
        """
        # 1. Generate current energy summary from database
        summary_response = EnergyDataService.get_summary()
        summary_data = summary_response.model_dump()

        # 2. Build system prompt with injected context
        system_prompt = build_system_prompt(summary_data)

        # 3. Generate conversation ID if absent
        conv_id = request.conversation_id or str(uuid.uuid4())

        # 4. Check OpenAI API availability
        client = cls._get_openai_client()
        now_str = datetime.now(timezone.utc).isoformat()

        if client is None or not settings.OPENAI_API_KEY:
            # Deterministic local rule-based response when OpenAI API Key is not set
            reply = cls._generate_mock_or_offline_reply(request.message, summary_data)
            from app.services.conversation_service import ConversationService
            ConversationService.record_chat_exchange(conv_id, request.message, reply)
            return ChatResponse(
                conversation_id=conv_id,
                reply=reply,
                used_summary=True,
                tool_calls_made=[],
                created_at=now_str
            )

        try:
            # Build initial messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ]

            tool_calls_log: List[Dict[str, Any]] = []   # tool 호출 기록 저장용 리스트

            # Function Calling loop (max 3 iterations to prevent infinite loops)
            max_iterations = 3
            for iteration in range(max_iterations):
                response = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    tools=TOOL_DEFINITIONS,     # AI에게 사용 가능한 함수 목록을 알려줌 (AI가 실행하는 것이 아닌, 특정 함수를 호출하고 싶다고 요청만 함. 실제 실행은 서버 코드가 함.)
                    tool_choice="auto",         # AI가 알아서 판단
                    temperature=0.1,            # 답변의 랜덤성/창의성 낮춤. 낮을수록 더 안정적/일관된 답변. 데이터 분석/조회에는 낮은 값. 
                    max_tokens=800              # 응답 길이 제한
                )

                assistant_message = response.choices[0].message     # AI 이번 턴 답변; assistant_message에는 AI 일반 답변(content) 또는 호출 정보(tool_calls)가 있을 수 있음 

                tool_calls = getattr(assistant_message, "tool_calls", None)     # assistant_message.tool_calls가 있으면 가져옴

                # If no tool calls, we have the final answer. AI가 tool을 요청하지 않았다면 이미 최종 답변을 했다는 뜻
                if not tool_calls:
                    reply = assistant_message.content.strip() if assistant_message.content else ""
                    break

                # Process tool calls
                # Append assistant message with tool_calls to conversation. AI가 “함수를 호출하고 싶다”고 한 내용을 대화 기록에 추가
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,       # e.g.) "get_energy_statistics"
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                for tool_call in assistant_message.tool_calls:      # tool_call이 보통 1개겠지만, 여러 개일 가능성도 있으므로 반복문
                    func_name = tool_call.function.name             # e.g.) "get_energy_data_by_date", "get_energy_statistics"
                    try:
                        func_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        func_args = {}

                    logger.info(f"Tool call: {func_name}({func_args})")

                    # Execute the tool
                    executor = TOOL_EXECUTORS.get(func_name)        # TOOL_EXECUTORS는 보통 함수 이름 → 실제 실행 함수를 연결한 딕셔너리
                    if executor:
                        result = executor(func_args)                # 실제 함수 호출
                    else:
                        result = {"error": f"Unknown tool '{func_name}'."}

                    # Log the tool call. 어떤 tool이 호출되었는지 기록 리스트에 추가 (나중에 API 응답에 포함할 수도 있고, 디버깅에도 사용)
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

        except Exception as e:
            logger.error(f"OpenAI API invocation failed: {e}. Falling back to offline context-injected logic.")
            reply = cls._generate_mock_or_offline_reply(request.message, summary_data)
            from app.services.conversation_service import ConversationService
            ConversationService.record_chat_exchange(conv_id, request.message, reply)
            return ChatResponse(
                conversation_id=conv_id,
                reply=reply,
                used_summary=True,
                tool_calls_made=[],
                created_at=now_str
            )

    @staticmethod
    def _generate_mock_or_offline_reply(user_msg: str, summary: Dict[str, Any]) -> str:
        """
        Offline fallback matching anti-hallucination rules for testing environments without active API keys.
        """
        msg = user_msg.lower()
        overall = summary.get("overall", {})
        extremes = summary.get("extremes", {})
        period = summary.get("period", {})
        trend = summary.get("trend", {})
        dow = summary.get("day_of_week", {})
        ww = summary.get("weekday_weekend", {})
        monthly = summary.get("monthly", {})
        breakdown = monthly.get("monthly_breakdown", {})
        cost = summary.get("cost", {})

        # Check for specific month queries (e.g. "July 2026", "2026-07", "7월")
        month_names_map = {
            "january": "01", "february": "02", "march": "03", "april": "04",
            "may": "05", "june": "06", "july": "07", "august": "08",
            "september": "09", "october": "10", "november": "11", "december": "12",
            "jan": "01", "feb": "02", "mar": "03", "apr": "04",
            "jun": "06", "jul": "07", "aug": "08", "sep": "09",
            "oct": "10", "nov": "11", "dec": "12",
            "1월": "01", "2월": "02", "3월": "03", "4월": "04",
            "5월": "05", "6월": "06", "7월": "07", "8월": "08",
            "9월": "09", "10월": "10", "11월": "11", "12월": "12"
        }

        matched_ym = None
        # Only treat as single month query if NOT a specific full date (YYYY-MM-DD),
        # NOT a date range query ("between", "from", "to", "weeks"), and NOT comparing multiple months ("and", "compare", "vs")
        is_full_date = bool(re.search(r"\b\d{4}-\d{2}-\d{2}\b", msg))
        is_range_query = any(k in msg for k in ["between", "from", "to", "week", "weeks", "기간", "~", "부터", "까지"])
        is_compare_query = any(k in msg for k in ["compare", "difference", "vs", "versus", "비교", "차이"])

        # If it's a range or compare query, or mentions multiple months, don't hijack with single-month summary
        found_months = [m_word for m_word in month_names_map.keys() if re.search(r"(?:\b|_)" + re.escape(m_word) + r"(?:\b|_)", msg)]
        is_multi_month = len(set(month_names_map[m] for m in found_months if m in month_names_map)) > 1

        if not is_full_date and not is_range_query and not is_compare_query and not is_multi_month:
            # Check standard YYYY-MM pattern
            ym_match = re.search(r"\b(202\d)-(0[1-9]|1[0-2])\b", msg)
            if ym_match:
                matched_ym = f"{ym_match.group(1)}-{ym_match.group(2)}"
            else:
                # Check month name words
                for m_word, m_num in month_names_map.items():
                    if re.search(r"(?:\b|_)" + re.escape(m_word) + r"(?:\b|_)", msg):
                        # Default year to 2026 if not specified
                        year_match = re.search(r"\b(202\d)\b", msg)
                        target_year = year_match.group(1) if year_match else "2026"
                        candidate_ym = f"{target_year}-{m_num}"
                        if candidate_ym in breakdown:
                            matched_ym = candidate_ym
                            break
                        elif f"2026-{m_num}" in breakdown:
                            matched_ym = f"2026-{m_num}"
                            break

        if matched_ym and matched_ym in breakdown:
            m_data = breakdown[matched_ym]
            m_avg = m_data.get("average_daily_consumption_kwh")
            m_tot = m_data.get("total_consumption_kwh")
            m_days = m_data.get("days_count")
            return (
                f"During {matched_ym}, your average daily electricity consumption was {m_avg} kWh/day "
                f"(total: {m_tot} kWh across {m_days} days)."
            )

        if "highest" in msg or "maximum" in msg or "최대" in msg or "가장 많이" in msg:
            if "month" in msg or "월" in msg:
                h_month = monthly.get("highest_total_month", {})
                return f"The month with the highest electricity usage was {h_month.get('month')} with a total of {h_month.get('total_consumption_kwh')} kWh."
            max_day = extremes.get("maximum_day", {})
            return f"Your highest consumption day was {max_day.get('date')} ({max_day.get('day_of_week')}) with {max_day.get('consumption_kwh')} kWh."

        if "lowest" in msg or "minimum" in msg or "최소" in msg or "가장 적게" in msg:
            if "month" in msg or "월" in msg:
                l_month = monthly.get("lowest_average_month", {})
                return f"The month with the lowest average electricity usage was {l_month.get('month')} with an average of {l_month.get('average_daily_consumption_kwh')} kWh/day."
            min_day = extremes.get("minimum_day", {})
            return f"Your lowest consumption day was {min_day.get('date')} ({min_day.get('day_of_week')}) with {min_day.get('consumption_kwh')} kWh."

        if "month" in msg or "월별" in msg or "월" in msg:
            h_month = monthly.get("highest_total_month", {})
            return f"The month with the highest electricity usage was {h_month.get('month')} with a total of {h_month.get('total_consumption_kwh')} kWh."

        if "average" in msg or "평균" in msg:
            return f"Your overall average daily electricity consumption is {overall.get('average_daily_consumption_kwh')} kWh/day across {period.get('duration_days')} days ({period.get('start_date')} to {period.get('end_date')})."

        if "lowest" in msg or "minimum" in msg or "최소" in msg or "가장 적게" in msg:
            min_day = extremes.get("minimum_day", {})
            return f"Your lowest consumption day was {min_day.get('date')} ({min_day.get('day_of_week')}) with {min_day.get('consumption_kwh')} kWh."

        if "weekend" in msg or "weekday" in msg or "주말" in msg or "평일" in msg:
            return f"Your weekday average is {ww.get('weekday_average_kwh')} kWh/day and weekend average is {ww.get('weekend_average_kwh')} kWh/day ({ww.get('pattern_description')})."

        if "trend" in msg or "추세" in msg or "트렌드" in msg:
            st = trend.get("short_term_trend", {})
            ot = trend.get("overall_trend", {})
            return f"Short-term trend (last 7 days): {st.get('direction')} ({st.get('percentage_change')}%), Overall trend: {ot.get('direction')} (linear slope: {ot.get('linear_slope_kwh_per_day')} kWh/day)."

        if "cost" in msg or "비용" in msg or "요금" in msg:
            return f"Total estimated cost is £{cost.get('total_estimated_cost_gbp')} ({cost.get('total_estimated_cost_pence')}p). Note: {cost.get('disclaimer')}."

        # Specific dates or outside range
        return (
            f"I only have access to high-level summary metrics for the period {period.get('start_date')} to {period.get('end_date')}. "
            "Specific single-day details or data outside this period are not included in the summary and require a direct database query."
        )
